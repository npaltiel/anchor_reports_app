import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from spire.xls import *
from spire.xls.common import *
import tempfile
import io

def main(visits, patients, contracts):
    visits_df = pd.read_csv(visits,low_memory=False)
    df_patients = pd.read_csv(patients)
    df_contracts = pd.read_csv(contracts)

    visits_df = visits_df[visits_df['MissedVisit'] == 'No']

    # Patient Churn
    # Split patient name and admission id
    split_df = visits_df['PatientName'].str.split('(', expand=True)
    split_df[1] = split_df[1].str.replace(')', '')
    visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

    # Lookup contracts and patient information from relevant sources
    visits_df = pd.merge(visits_df, df_contracts, on='ContractName', how='left')
    visits_df['ContractType'] = visits_df['ContractType'].fillna('Unknown')

    visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')

    visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.lstrip('0')

    # Create unique ID
    visits_df['UniqueID'] = [
    visits_df['MedicaidNo'][i] if pd.notna(visits_df['MedicaidNo'][i]) else visits_df['PatientName'][
                                                                            i] + str(
    visits_df['DOB'][i]) for i in range(len(visits_df))]

    # Create Baby Branch
    visits_df['Branch_Updated'] = [
    'Baby' if pd.notna(visits_df['DOB'][i]) and
            datetime.strptime(visits_df['DOB'][i].strip(),
                            "%m/%d/%Y %H:%M").date() >= date.today() - relativedelta(years=2)
    else visits_df['Branch'][i]
    for i in range(len(visits_df))
    ]

    today = datetime.now()
    sixteenth_of_previous_month = (today.replace(day=1) - pd.DateOffset(months=1)).replace(day=16).date()

    visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
    prev_df = visits_df[visits_df['VisitDate'] < pd.Timestamp(sixteenth_of_previous_month)]
    cur_df = visits_df[visits_df['VisitDate'] >= pd.Timestamp(sixteenth_of_previous_month)]

    # Drop duplicates based on Unique ID
    prev_df = prev_df.sort_values(by=['VisitDate'])
    prev_df = prev_df.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)
    cur_df = cur_df.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)

    prev_ids = []
    for i in range(len(prev_df)):
        prev_ids.append(prev_df['UniqueID'][i])

    soc_df = cur_df[~cur_df['UniqueID'].isin(prev_ids)][
    ['AdmissionID', 'First Name', 'Last Name', 'VisitDate', 'Branch_Updated', 'ContractName', 'ContractType', 'Team',
    'DOB', 'Status']].copy()

    soc_df.rename(columns={'VisitDate': 'FirstVisitDate'}, inplace=True)

    # Output Excel file path
    month = datetime.today().strftime('%b')
    year = datetime.today().strftime('%Y')
    
    # Prepare file to be downloadable in the App
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        temp_filename = tmp_file.name
    
    # Save DataFrame to the temporary Excel file
    with pd.ExcelWriter(temp_filename, engine='xlsxwriter') as writer:
        soc_df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.book.close()

    workbook = Workbook()
    workbook.LoadFromFile(temp_filename)

    data_sheet = workbook.Worksheets[0]
    rnge = 'A1:J' + str(len(soc_df) + 1)
    cellRange = data_sheet.Range[rnge]

    # Create Pivot Table
    pivotCache = workbook.PivotCaches.Add(cellRange)
    pivot_sheet = workbook.Worksheets.Add("Pivot")
    pivotTable = pivot_sheet.PivotTables.Add("Pivot Table", pivot_sheet.Range["B3"], pivotCache)

    pivotTable.Options.RowHeaderCaption = "Row Labels"
    pivotTable.PivotFields["Team"].Axis = AxisTypes.Row
    pivotTable.PivotFields["Status"].Axis = AxisTypes.Column
    pivotTable.DataFields.Add(pivotTable.PivotFields["AdmissionID"], "SOC Count", SubtotalTypes.Count)
    pivotTable.CalculateData()
    pivotTable.PivotFields["Team"].SortType = PivotFieldSortType.Ascending
    pivotTable.BuiltInStyle = PivotBuiltInStyles.PivotStyleMedium11

    # Save workbook to another temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_final:
        final_filename = tmp_final.name
    workbook.SaveToFile(final_filename, ExcelVersion.Version2016)
    workbook.Dispose()

    # Save workbook to a new BytesIO stream
    processed_file = io.BytesIO()
    with open(final_filename, "rb") as f:
        processed_file.write(f.read())

    # Clean up temporary files
    os.remove(temp_filename)
    os.remove(final_filename)

    processed_file.seek(0)

    return (f"Report Run for {month} {year}", processed_file)
