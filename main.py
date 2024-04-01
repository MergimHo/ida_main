import uvicorn
from starlette.responses import RedirectResponse, JSONResponse
from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from typing import Optional, List
from csv import reader
from io import StringIO
import logging as log


### gloabls
app = FastAPI()
indices = []
valid_indices = ["DAX" , "SP500", "ALL"]
log.basicConfig(level=log.DEBUG)

@app.get("/health")
async def health():
  log.info("Executing Health Check.")
  return JSONResponse(status_code=200, content={"message": "Application is running."})

@app.get("/")
async def redirect():
  response = RedirectResponse(url='/docs')
  return response

@app.get("/getdata/{date}")
async def read_item(date: str, index: str = "DAX", show_all_indices: Optional[bool] = False):
  result = {"date": date}

  if date not in fake_items_db:
        raise HTTPException(status_code=404, detail="Date not found")

  elif show_all_indices:
    for i in indices:
      result.update({i: fake_items_db[date][i]})

  else:
    result.update({index: fake_items_db[date][index]})

  return result


"""
Exercise 1: Get All Data By Index separated page by page with 30 entries by page
Input parameter: 'DAX', 'SP500' or 'ALL'.
"""
@app.get("/getdata/")
async def read_item(index: str = Query("ALL", description="Index parameter, either 'DAX', 'SP500' or 'ALL'.")):

  index = index.upper() if index else None

  if index not in valid_indices or index is None:
    log.error(f"Unknown parameter '{index}' was given. Valid are 'DAX', 'SP500' and 'ALL'.")
    raise HTTPException(status_code=400, detail="Invalid Index parameter. Please choose 'DAX', 'SP500' or 'ALL'.")


  log.info(f"Searching and Paginating for index {index}")
  result = []
  page_number = 1
  page = {page_number: []}

  for indice_counter, (date, indices) in enumerate(fake_items_db.items(), start=1):

    current_share = (date, indices if index == "ALL" else indices.get(index))
    page[page_number].append(current_share)

    if indice_counter % 30 == 0 or indice_counter == len(fake_items_db):
      result.append(page)
      page_number = page_number + 1
      page = {page_number: []}

  log.info("Request was succesfull.") 
  return JSONResponse(status_code=200, content=result, headers={"requested-index": index})

"""
Exercise 1: Get All Data separated page by page with 30 entries by page
"""
@app.get("/getdataAll")
async def read_item_all():
  log.info("Redirecting to /getdata with parameter 'ALL'")
  return RedirectResponse(url='/getdata?index=ALL')

"""
Exercise 2: Upload file with csv.

"""
@app.post("/uploadfile/")
async def create_upload_files(file: UploadFile = File(...)):
  # add the entries of the uploaded file to fake_items_db
  # data structure of fake_items_db:
  # {"09091990": {"DAX": "1232456", "SP500:" "9238748"}, "08081990":{"DAX": "2345646", "SP500:" "2324432"}, ..}
  global fake_items_db

  if not file or file.size == 0:
      log.error("File empty.")
      raise HTTPException(status_code=400, detail="No file uploaded.")
  elif file.content_type not in ['application/vnd.ms-excel', 'text/csv'] and not file.filename.lower().endswith('.csv'):
    log.error("No CSV data reiceived")
    raise HTTPException(415, "Only CSV data allowed. File ending must be *.csv or correct content-type.")

  log.info(f"Received uploaded file {file.filename}. Now trying to update.")

  try: 
    content = await file.read()
    contents_io = StringIO(content.decode('utf-8-sig'))
    csv_reader = reader(contents_io)
    csv_data = [row for row in csv_reader]
    add_entries_to_dict(csv_data)
    fake_items_db = dict(sorted(fake_items_db.items(), reverse=True))
    log.info(f"Updated {len(csv_data[1:])} entries.")
  except Exception as e:
        log.error("File was uploaded and a CSV but its content could not be processed due to invalid entries.")
        return JSONResponse(status_code=400, content={"message": "The request contained non-valid CSV data."})

  return JSONResponse(status_code=201, content={"message": "The Shared Indices were succesfully updated."})

def add_entries_to_dict(data):
  """
  Adds the entries to the global fake_items_db dictionairy.
  Only available during server runtime.

  Args:
      data (list(list)): [["Date", "DAX", "SP501"], ["30112021", "132345", "762190"], ..]
  """
  for line_no, line in enumerate(data, 0):
    if (line_no == 0):
      new_indices = line[1:]
      for index in new_indices:
        indices.append(index) if index not in indices else indices
        #todo: check order of line of line_no == 0 and indices
    else:
      fake_items_db.update({line[0]: {}})
      for index_no, index in enumerate(indices, 1):
        fake_items_db[line[0]].update({index: line[index_no + 0]})


def initialize_dict(fake_items_db, filename):
  """
  Initializes the fake_items_db dictionairy

  Args:
      fake_items_db (dict): initial empty dictionairy
      filename (string): path to inital file

  Returns:
      dict(dict): {"09091990": {"DAX": "1232456", "SP500:" "9238748"}, "08081990":{"DAX": "2345646", "SP500:" "2324432"} ..}
  """
  file = open('./' + filename, encoding='UTF8')
  csv_reader = reader(file)
  add_entries_to_dict(csv_reader)
  file.close()

  return fake_items_db

# Helper method for testing purposes.
def get_fake_items_db():
  return fake_items_db

@app.get("/testdb")
def get_fake_items_db():
  return dict(sorted(fake_items_db.items(), reverse=True))

@app.get("/refreshdb")
def get_fake_items_db():
  global fake_items_db
  fake_items_db = dict()
  fake_items_db = initialize_dict(fake_items_db=fake_items_db, filename="daxsp.csv")
  return JSONResponse(status_code=200, content={"message": "Database resetted back to initial state."})





fake_items_db = dict()
fake_items_db = initialize_dict(fake_items_db=fake_items_db, filename="daxsp.csv")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
