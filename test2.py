import pandas as pd

def loc(filename, sheetname):
    str=["China DC", "China Branch offices "]  
    if sheetname in str:   
        df = pd.read_excel( io=filename, sheet_name= sheetname, header = None)
        tables = []
        location = []
        location= df.iloc[1:,5].unique()
        for c in location: 
            table = df[df.iloc[:,5]==c]

            tables.append(table)

        return location, tables
         
    else:

        df = pd.read_excel( io=filename, sheet_name= sheetname, header = None)
        tables = []
        location = []

        location.append(df.iloc[1,0])
    

        cur_table_start = None

        

        for i, row in df.iterrows():
            if  not row.isna().all():
                if cur_table_start is None:
                    cur_table_start = i
                    if i!= 0:
                     location.append(df.iloc[i,0])
            
            else:
                if cur_table_start is not None:
                    table = pd.read_excel(io=filename, sheet_name= sheetname, header=0, skiprows = cur_table_start, nrows= i-cur_table_start)
                    tables.append(table)
                    cur_table_start = None

        if cur_table_start is not None:
            table = pd.read_excel( io=filename, sheet_name= sheetname, header=0, skiprows = cur_table_start, nrows= len(df)-cur_table_start)
            tables.append(table)  
        
        
        return location,tables
    

# loc('APAC_ network Inventory.xlsx', 'China DC')
# loc('APAC_ network Inventory.xlsx', 'India')
# loc('APAC_ network Inventory.xlsx', 'China Branch offices') 