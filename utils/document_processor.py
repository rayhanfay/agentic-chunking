from typing import Tuple, List, Optional, Dict, Any
import base64
import io
import fitz
import docx2txt
import PyPDF2
import pandas as pd
import camelot

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

class DocumentProcessor:
    def __init__(self, max_doc_size: int = 50 * 1024 * 1024):
        self.max_doc_size = max_doc_size
        
    def process_document(self, contents: any, filename: str) -> Tuple[Any, List[dict], List[pd.DataFrame], Optional[str]]:
        """
        Process uploaded document and extract content, images, and tables
        
        Returns:
        Tuple[Any, List[dict], List[pd.DataFrame], Optional[str]]: 
            - Processed content
            - List of extracted images
            - List of extracted tables
            - Plain text version for vectorization
        """
        try:
            # content_type, content_string = contents.split(",")
            # decoded = base64.b64decode(content_string)
            decoded = contents
            
            if len(decoded) > self.max_doc_size:
                raise ValueError("File too large (max 50MB)")
            
            if filename.lower().endswith('.pdf'):
                return self._process_pdf(decoded)
            elif filename.lower().endswith(('.txt', '.md')):
                content = decoded.decode("utf-8")
                return content, [], [], content
            elif filename.lower().endswith('.docx'):
                content = docx2txt.process(io.BytesIO(decoded))
                return content, [], [], content
            else:
                raise ValueError("Unsupported file type")
                
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")

    def _process_pdf(self, pdf_bytes: bytes) -> Tuple[List[List[dict]], List[dict], List[pd.DataFrame], str]:
        """Process PDF file and extract content, images, and tables"""
        content = self._extract_text_with_layout(pdf_bytes)
        images = self._extract_images(pdf_bytes)
        tables = self._extract_tables(pdf_bytes)
        
        # Create plain text version for vectorstore
        plain_text = "\n".join(
            " ".join(span["text"] for spans in page for span in spans)
            for page in content
        )
        
        return content, images, tables, plain_text
    
    def _extract_text_with_layout(self, pdf_bytes: bytes) -> List[List[dict]]:
        """Extract text from PDF while preserving layout"""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages_content = []
            
            for page in doc:
                blocks = page.get_text("dict", sort=True)["blocks"]
                page_text = []
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            if "spans" in line:
                                spans_text = []
                                for span in line["spans"]:
                                    if span["text"].strip():
                                        spans_text.append({
                                            "text": span["text"],
                                            "font_size": span["size"],
                                            "is_bold": "bold" in span["font"].lower(),
                                            "is_italic": "italic" in span["font"].lower(),
                                            "bbox": span["bbox"]
                                        })
                                
                                if spans_text:
                                    page_text.append(spans_text)
                
                pages_content.append(page_text)
                
            return pages_content
            
        except Exception as e:
            raise Exception(f"Error in PDF text extraction: {e}")
    
    def _extract_images(self, pdf_bytes: bytes) -> List[dict]:
        """Extract images from PDF"""
        images = []
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_format = base_image["ext"]
                        
                        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                        
                        images.append({
                            'data': f"data:image/{image_format};base64,{image_b64}",
                            'page': page_num,
                            'format': image_format,
                            'size': len(image_bytes)
                        })
                        
                    except Exception as e:
                        print(f"Error extracting image {img_index + 1} from page {page_num + 1}: {str(e)}")
                        continue
                        
            return images
            
        except Exception as e:
            raise Exception(f"Error extracting images: {str(e)}")
    
    def _extract_tables(self, pdf_bytes: bytes) -> List[pd.DataFrame]:
        """Extract tables from PDF"""
        try:
            if CAMELOT_AVAILABLE:
                return self._extract_tables_camelot(pdf_bytes)
            else:
                return self._extract_tables_basic(pdf_bytes)
                
        except Exception as e:
            raise Exception(f"Error extracting tables: {str(e)}")
    
    def _extract_tables_camelot(self, pdf_bytes: bytes) -> List[pd.DataFrame]:
        """Extract tables using Camelot library"""
        pdf_buffer = io.BytesIO(pdf_bytes)
        tables = camelot.read_pdf(pdf_buffer, pages='all', flavor='stream')
        extracted_tables = []
        
        for table in tables:
            df = table.df
            # Clean up the dataframe
            df = df.replace(r'\n', ' ', regex=True)
            df = df.replace(r'\s+', ' ', regex=True)
            df = df.dropna(axis=1, how='all')
            df = df.loc[:, (df != '').any()]
            df = df.dropna(how='all')
            df.columns = [f"Column {i+1}" for i in range(len(df.columns))]
            
            if not df.empty:
                extracted_tables.append(df)
        
        return extracted_tables
    
    def _extract_tables_basic(self, pdf_bytes: bytes) -> List[pd.DataFrame]:
        """Basic table extraction when Camelot is not available"""
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        
        tables = []
        for page in reader.pages:
            text = page.extract_text()
            rows = [line.split() for line in text.split('\n') if line.strip()]
            if rows:
                df = pd.DataFrame(rows)
                if not df.empty:
                    tables.append(df)
        
        return tables