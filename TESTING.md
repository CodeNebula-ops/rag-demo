# Testing Guide — AI Knowledge Base RAG System

This guide walks through every feature of the system with step-by-step test cases. Run these after the system is up at `http://localhost:3000` (local) or your Render URL.

## Prerequisites

- System is running (`docker compose up --build` completed)
- Backend API accessible at `http://localhost:8000/docs` (Swagger UI)
- Frontend accessible at `http://localhost:3000`

---

## Test 1: Health Check

**Goal**: Verify all services are connected.

**Via Swagger UI**:
1. Open http://localhost:8000/docs
2. Click `GET /api/v1/health` → "Try it out" → "Execute"
3. Verify response:
```json
{
  "status": "ok",
  "postgres": "ok",
  "qdrant": "ok",
  "llm": "ok"
}
```

**Via Frontend**:
1. Open http://localhost:3000
2. Check bottom-left sidebar — all three status dots (Backend, LLM, Vector DB) should be green

**Via curl**:
```bash
curl http://localhost:8000/api/v1/health
```

**Troubleshooting**:
- `postgres: error` → Check if PostgreSQL container is running: `docker ps`
- `qdrant: error` → Verify QDRANT_HOST and QDRANT_API_KEY in `.env`
- `llm: error` → Verify GROQ_API_KEY in `.env` is valid

---

## Test 2: Upload a Document

**Goal**: Upload a PDF/TXT/DOCX and verify it gets processed into chunks.

### Prepare a test file

Create a file called `test_document.txt` with this content:
```
# Company Leave Policy

## Annual Leave
All employees are entitled to 25 days of annual leave per calendar year.
Leave must be requested at least 2 weeks in advance through the HR portal.
Unused leave cannot be carried over to the next year beyond 5 days.

## Sick Leave
Employees receive 12 days of paid sick leave per year.
A medical certificate is required for absences exceeding 3 consecutive days.
Sick leave cannot be used as annual leave.

## Maternity Leave
Female employees are entitled to 90 days of paid maternity leave.
An additional 30 days of unpaid leave may be requested.
The employee must notify HR at least 30 days before the expected date.

## Emergency Leave
Up to 5 days of paid emergency leave per year for immediate family emergencies.
Documentation must be submitted within 7 days of returning to work.
Emergency leave cannot be pre-planned or scheduled.

## Work From Home Policy
Employees may work from home up to 2 days per week with manager approval.
A stable internet connection and dedicated workspace are required.
Core hours of 10:00 AM to 4:00 PM must be maintained during WFH days.
```

### Upload via Frontend
1. Go to http://localhost:3000
2. Click "Documents" in the sidebar
3. Drag and drop `test_document.txt` onto the upload zone (or click to browse)
4. Watch the upload progress bar
5. Verify the document appears in the list with status "processing" (yellow, pulsing)
6. Wait ~10-30 seconds — status should change to "active" (green)
7. Check that "Chunks" column shows a number > 0 (likely 5-8 chunks)

### Upload via curl
```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@test_document.txt"
```

Expected response:
```json
{
  "id": "uuid-here",
  "title": "Test Document",
  "filename": "test_document.txt",
  "file_type": "txt",
  "status": "processing",
  "total_chunks": 0,
  ...
}
```

### Verify processing completed
```bash
curl http://localhost:8000/api/v1/documents
```
The document should now show `"status": "active"` and `"total_chunks"` > 0.

---

## Test 3: Ask a Question That IS in the Document

**Goal**: Get an accurate, cited answer from the knowledge base.

### Via Frontend
1. Click "Chat" in the sidebar
2. Click "Start a conversation" (or "New Chat")
3. Type: `How many days of annual leave do employees get?`
4. Press Enter
5. Verify:
   - Answer streams in token by token
   - Answer mentions "25 days"
   - A `[Source: ...]` citation appears
   - A confidence badge shows (should be "High" or "Medium")
   - A "sources" link appears — click it to see the citation panel

### Via curl
```bash
# Create a session
curl -X POST http://localhost:8000/api/v1/chat/sessions \
  -H "Content-Type: application/json" \
  -d '{}'

# Use the session ID from the response
curl -X POST http://localhost:8000/api/v1/chat/sessions/SESSION_ID_HERE/messages \
  -H "Content-Type: application/json" \
  -d '{"query": "How many days of annual leave do employees get?"}'
```

The SSE stream will contain token, citation, confidence, and done events.

---

## Test 4: Ask a Question NOT in Any Document

**Goal**: System should refuse to answer and not hallucinate.

1. In the same chat session (or a new one), type:
   `What is the company's stock price?`
2. Verify the response says something like:
   - "I don't have enough information in the knowledge base to answer this question"
   - OR "No relevant information found in the knowledge base"
3. Confidence badge should show "Low" (red)

**Try more out-of-scope questions**:
- `Who is the CEO of the company?`
- `What programming language should I use for the backend?`
- `What is the meaning of life?`

All should be declined or flagged as low confidence.

---

## Test 5: Follow-up / Conversation Context

**Goal**: Verify the system maintains conversation context.

1. In a chat session, ask: `What is the maternity leave policy?`
2. Wait for the answer
3. Follow up with: `How much of it is paid?`
4. Verify:
   - The system understands "it" refers to maternity leave
   - The answer correctly states "90 days paid" and "30 days unpaid"
   - Citations are present

---

## Test 6: Confidence Scoring

**Goal**: Verify confidence levels display correctly.

### High confidence
Ask: `How many sick leave days do employees get per year?`
- Expected: Direct factual answer, "High confidence" badge (green)

### Low confidence
Ask: `What are the penalties for excessive absenteeism?`
- Expected: This isn't in the document, so the system should either decline or answer with "Low confidence" badge (red) and a warning

### Medium confidence
Ask: `Can I work from home on Fridays?`
- Expected: The WFH policy section is relevant but doesn't mention specific days — may get "Medium confidence" (yellow)

---

## Test 7: Delete a Document

**Goal**: Verify deleted documents are no longer used in retrieval.

1. Go to "Documents" in the sidebar
2. Click the trash icon next to "Test Document"
3. Click trash icon again to confirm
4. Status should change to "archived"
5. Go back to "Chat" and ask: `How many days of annual leave?`
6. Verify the system can no longer answer this question (should say "no relevant information" or very low confidence)

---

## Test 8: Multi-Document Upload and Cross-Document Queries

**Goal**: Verify the system can pull from multiple sources.

### Create a second test file `it_policy.txt`:
```
# IT Security Policy

## Password Requirements
All passwords must be at least 12 characters long.
Passwords must include uppercase, lowercase, numbers, and special characters.
Passwords must be changed every 90 days.
Previous 5 passwords cannot be reused.

## VPN Access
All remote access to company systems must use the company VPN.
VPN credentials are provided by the IT department.
Employees must not share VPN credentials.

## Device Policy
Company laptops must have full-disk encryption enabled.
Personal devices may not be used to access company email or documents.
All company devices must have antivirus software installed.

## Data Classification
All company data is classified as: Public, Internal, Confidential, or Restricted.
Confidential and Restricted data must not be stored on personal devices.
Sharing Restricted data requires written approval from the department head.
```

### Test steps
1. Upload `it_policy.txt` via the Documents page
2. Wait for status to become "active"
3. Ask: `What are the password requirements?`
   - Should cite the IT Security Policy document
4. Ask: `Can I access company email from my personal phone?`
   - Should cite the Device Policy section saying personal devices cannot be used
5. Ask: `What is the policy about taking time off and working remotely?`
   - Should cite BOTH documents (leave policy + WFH from HR doc, VPN from IT doc)
   - Check that multiple source citations appear

---

## Test 9: Feedback System

**Goal**: Verify thumbs up/down feedback is recorded.

1. In any chat, find an AI response
2. Click the thumbs-down icon at the bottom of the message
3. The icon should turn red (selected state)
4. Click thumbs-up on another message
5. That icon should turn green

### Verify via API
```bash
curl http://localhost:8000/api/v1/chat/sessions/SESSION_ID/history
```
Messages should include `"feedback": "up"` or `"feedback": "down"`.

---

## Test 10: Analytics Dashboard

**Goal**: Verify analytics reflect actual usage.

1. Click "Analytics" in the sidebar
2. Check "Usage Overview" cards:
   - **Total Queries** should match how many questions you've asked
   - **Queries Today** should be > 0
   - **Avg Confidence** should be a percentage
   - **Avg Latency** should be reasonable (typically 1-5 seconds)
3. Check "Content Gaps" section:
   - Any questions you asked that got low confidence should appear here
   - These represent topics where more documents should be uploaded

### Verify via API
```bash
curl http://localhost:8000/api/v1/analytics/usage
curl http://localhost:8000/api/v1/analytics/content-gaps
```

---

## Test 11: File Type Support

**Goal**: Verify different file types can be uploaded.

Test with each supported format:
1. `.txt` — plain text (tested above)
2. `.md` — markdown file with headings
3. `.pdf` — any PDF document
4. `.docx` — any Word document

For each:
- Upload should succeed
- Status should reach "active"
- Chunks count should be > 0
- Asking questions about the content should return relevant answers

### Unsupported file test
Try uploading a `.jpg` or `.xlsx` file:
- Should get a 400 error: "Unsupported file type"

---

## Test 12: Streaming Behavior

**Goal**: Verify real-time token streaming works.

1. Ask a long question that requires a detailed answer:
   `Summarize all the leave types available and their durations.`
2. Watch the chat — tokens should appear one by one (not all at once)
3. During streaming:
   - The input box should be disabled
   - The send button should be grayed out
4. After streaming completes:
   - Citations appear
   - Confidence badge appears
   - Feedback buttons appear
   - Input box re-enables

---

## Test 13: Edge Cases

### Empty query
- Try sending an empty message → should be blocked by the input (min 1 char)

### Very long query
- Type 2000+ characters → character counter should cap at 2000

### Special characters
- Ask: `What's the policy for "emergency" leave (if any)?`
- Should handle quotes and parentheses correctly

### Rapid-fire questions
- Ask a question, then immediately ask another before the first finishes
- The second should be blocked while streaming (button disabled)

---

## Quick Smoke Test Checklist

Run through this in 5 minutes to verify everything works:

| # | Action | Expected Result |
|---|--------|----------------|
| 1 | Open http://localhost:3000 | App loads, sidebar visible |
| 2 | Check health dots (bottom-left) | All three green |
| 3 | Go to Documents | Upload zone visible |
| 4 | Upload `test_document.txt` | Status becomes "active" |
| 5 | Go to Chat → New Chat | Empty chat appears |
| 6 | Ask "How many annual leave days?" | Answer says 25, has citation |
| 7 | Ask "What's the stock price?" | Declines or shows low confidence |
| 8 | Click thumbs-up on an answer | Icon highlights |
| 9 | Go to Analytics | Stats cards show data |
| 10 | Delete the document | Status changes to "archived" |
