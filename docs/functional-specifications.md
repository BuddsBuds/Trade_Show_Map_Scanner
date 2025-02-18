# TradeShow Scout - Functional Specifications  
**Version**: 1.0  

---

## **1. File Processing Service**  
- **Input**: PDF/JPG/PNG (single or multi-file).  
- **Output**: Stitched image (for fragmented uploads).  
- **Tools**: OpenCV (stitching), PyPDF2 (PDF parsing).  

## **2. OCR & Data Extraction**  
- **Workflow**:  
  1. Preprocess image (auto-rotate, contrast adjustment).  
  2. Extract text via Tesseract OCR.  
  3. Default booth size: `10x10ft` if unlabeled.  

## **3. Contact Scraping Service**  
- **APIs**: Hunter.io (emails), LinkedIn (titles/profiles).  
- **Rate Limits**: Celery queues for API throttling.  

## **4. Frontend (React SPA)**  
- **Features**:  
  - Drag-and-drop upload with progress bar.  
  - Editable table for data correction.  
  - CSV export with confidence scores.  

---

## **Workflows**  
1. **User Upload** → File stitching → OCR → Contact scraping → CSV export.  
2. **Admin**: Monitor API usage and system health.