from flask import Flask, request,render_template, redirect,url_for, send_from_directory
import pandas as pd
import test2
import os
from flask_session import Session
from flask import *
import atexit

app = Flask(__name__)
 
 

app.secret_key = "none"
 
 


    
 

strn=["China DC", "China Branch offices "] #creating two exception cases since the formatting in these two spreadsheet is different from the default template

processed_files= 'processed_files.txt'

def get_processed_files():
    with open(processed_files,'r') as f:
         lines = f.readlines()
         return lines[-1].strip() if lines else None
    
def mark_file_as_processed(filename):
     with open(processed_files,'a') as f:
         f.write(filename +'\n')

eol_file= 'eol_files.txt'

def get_eol_files():
    with open(eol_file,'r') as f:
         lines = f.readlines()
         return lines[-1].strip() if lines else None
    
def mark_file_as_eol(filename):
     with open(eol_file,'a') as f:
         f.write(filename +'\n')




@app.route('/upload_page', methods=['GET', 'POST'])
def upp():
      return  render_template('upload.html')

#function for temporarily saving the file in a local space (for access and processing)

@app.route('/upload', methods=['GET', 'POST'])
def up():
    file = request.files['file']

    if file:
        file.save(file.filename)     
        file_path = os.path.join(file.filename)
        mark_file_as_processed(file_path)
       
    
    else :
       #error handling when the file is not uploaded
        flash("Please try uploading the file again.")
        return render_template('upload.html')
    
    return  redirect(url_for("show_table"))

#funtion to delete all the temporary files stored in local storage for processing
# def cleanup():
#     for file_path in temp_file:
#         if os.path.exists(file_path):
#             os.remove(file_path)
#             print("deleted")


#function to download the current data file from the browser.

@app.route('/download_excel', methods=['GET', 'POST'])
def down():
    try:
        file_name= get_processed_files()
        return send_from_directory("./",file_name, as_attachment= True)
    except Exception as e:
        return f"Error: {str(e)}", 404
    

# @app.route('/help', methods=['GET', 'POST'])
# def help_page():
#     return render_template('help.html')

@app.route('/eol', methods=['GET', 'POST'])
def eol_page():
    eol_path= get_eol_files()
    df = pd.ExcelFile(eol_path)
    sh= df.sheet_names 
    df = pd.read_excel(eol_path, sheet_name=sh[0],usecols=[0,1])
     
    df['EOL Details']= df['EOL Details'].apply(convert_date)
     
    table =  df.to_html(index = False)

    return render_template('eol_details.html', table=table)


def convert_date(value):
    try:
        return pd.to_datetime(value).strftime('%d-%m-%y')
    except Exception as e:
        return value
    
   

@app.route('/downloadeol', methods=['GET', 'POST'])
def down_eol():
    try:
        file_name= get_eol_files()
        return send_from_directory("./",file_name, as_attachment= True)
    except Exception as e:
        return f"Error: {str(e)}", 404

@app.route('/upload_eol', methods=['GET', 'POST'])
def up_eol():
    file = request.files['file']

    if file:
        file.save(file.filename)     
        file_path = os.path.join(file.filename)
        mark_file_as_eol(file_path)      
    
    else :
       #error handling when the file is not uploaded
        flash("Please try uploading the file again.")
        return render_template('eol_details.html')
    
    return  redirect(url_for("eol_page"))


 

#function to filter based on various parameters.

@app.route('/', methods=['GET', 'POST'])
def show_table():
     
    #initializing the variables that need to be returned back to the form
    
    file_path = get_processed_files()
    df = pd.ExcelFile(file_path)
     
    #initializing the variables that need to be returned back to the form
    sheet_names= df.sheet_names   
    
   
    selected_sheet = None

    model_class= None
    selected_model_class= None

    model_type= None
    selected_model_type= None

    location = None
    selected_location= None

    loc_tables= None

    mc_data= None
     
    dict_list =[]
    tot_router= None 

    no_filter_dict_list = []


    no_filter_sheet_name= sheet_names

    #in case region is also not selected

    for reg in no_filter_sheet_name:
        df = pd.read_excel(file_path, sheet_name=reg)
        no_filter_location,no_filter_loc_tables= test2.loc(file_path,reg)

        no_filter_region_dict_list=[]

        for i in range(len(no_filter_location)):
                 
                    city= no_filter_location[i]
                    
                    
                    if i == 0 and reg not in strn:
                        
                        no_filter_no_router= len(no_filter_loc_tables[i]) -1
                    else:
                        no_filter_no_router=len(no_filter_loc_tables[i])

                    no_filter_region_dict = {'city': city, 'no_router':no_filter_no_router}
                    no_filter_region_dict_list.append(no_filter_region_dict)

        no_filter_tot_router= 0
        for d in no_filter_region_dict_list:
            nr= d['no_router']
            no_filter_tot_router+=nr
        
        no_filter_dict ={'region':reg,'lists':no_filter_region_dict_list, 'tot_router':no_filter_tot_router}
        no_filter_dict_list.append(no_filter_dict)


     
      
     
   
     
#for recursively filtering the data based on the changes on of the menu of the filtering form
    if request.method == 'POST':
        #getting values from the from
        selected_sheet = request.form.get('sheet')
        selected_model_class = request.form.getlist('model_class')
        selected_model_type = request.form.getlist('model_type')
        selected_location = request.form.getlist('location')
         

        df = pd.read_excel(file_path, sheet_name=selected_sheet)
       

        #for diplaying the values in the form once selected the required sheet
        model_class= df.iloc[:,2].unique()         
        model_type = df.iloc[:,3].unique()
         

        location,loc_tables= test2.loc(file_path,selected_sheet)

        


       
        if selected_location:
             
            dict_list =[]
            model_class=[]
            model_type=[]
            mc_data=[]
            table = None
            #for setting the router no. when only the location is input
            for i in range(len(location)):
                 
                if location[i] in selected_location:
                              
                    city= location[i]
                    
                    
                    if i == 0 and selected_sheet not in strn:
                        
                        no_router= loc_tables[i].shape[0]-1
                    else:
                        no_router= loc_tables[i].shape[0]

                    # temptab= loc_tables[i].dropna() 
                    temptab= loc_tables[i] 
                     
                    table = temptab.to_html(classes = 'data-table',index = False)

                    

                    model_class.extend(loc_tables[i].iloc[:,2].unique())
                    model_type.extend(loc_tables[i].iloc[:,3].unique())

                    #filtering conditions                    
                    if selected_model_class and not selected_model_type: 
                        
                        
                       
                        for mc in selected_model_class:
                            temp= loc_tables[i][(loc_tables[i].iloc[:,2]==mc)]
                            mt= temp.iloc[:,3].unique()
                            
                            for t in mt:                                
                                tf = temp[temp.iloc[:,3]==t]                                                               
                                num= tf.shape[0]
                                tb= tf.to_html( index = False)
                                mc_data.append({'city':city,'class':mc, 'type':t, 'num':num, 'tb':tb})
                            
                            
                        
                        

                        loc_tables[i]= loc_tables[i][(loc_tables[i].iloc[:,2].isin(selected_model_class))]
                        table = loc_tables[i].to_html(classes = 'data-table',index = False)
                        model_type=[]  

                        for j in range(len(location)):                 
                            if location[j] in selected_location:                    
                                 model_type.extend(loc_tables[j].iloc[:,3].unique())
                        
                                   
                     
                     

                    elif selected_model_type and not selected_model_class:
                        
                        
                        for t in selected_model_type:
                            temp= loc_tables[i][(loc_tables[i].iloc[:,3]==t)]
                            
                            m= temp.iloc[:,2].unique()

                            for mc in m:                                
                                tf = temp[temp.iloc[:,2]==mc]                                
                                num= tf.shape[0]
                                tb= tf.to_html(classes = 'data-table',index = False)
                                mc_data.append({'city':city,'class':mc, 'type':t, 'num':num, 'tb':tb})
                        
                       
                        


                        loc_tables[i]= loc_tables[i][(loc_tables[i].iloc[:,3].isin(selected_model_type))]
                        table = loc_tables[i].to_html(classes = 'data-table',index = False)
                        
                        model_class=[] 
                        for j in range(len(location)):                 
                            if location[j] in selected_location:
                                model_class.extend(loc_tables[j].iloc[:,2].unique())                        
                                # print(model_class)

                    elif selected_model_type and selected_model_class:
                      
                         
                        temp= loc_tables[i][(loc_tables[i].iloc[:,2].isin(selected_model_class))&(loc_tables[i].iloc[:,3].isin(selected_model_type))]
                         
                       
                        m= temp.iloc[:,2].unique()
                        
                        for mc in m:
                            tf= temp[temp.iloc[:,2]==mc]
                            mt= tf.iloc[:,3].unique()
                            
                            for t in mt:                                
                                tf = temp[temp.iloc[:,3]==t]                                
                                
                                num= tf.shape[0]
                                tb= tf.to_html(classes = 'data-table',index = False)
                                mc_data.append({'city':city,'class':mc, 'type':t, 'num':num, 'tb':tb})                       


                        loc_tables[i]= loc_tables[i][(loc_tables[i].iloc[:,2].isin(selected_model_class))]
                        table = temp.to_html(classes = 'data-table',index = False)
                        model_type=[]  

                        for j in range(len(location)):                 
                            if location[j] in selected_location:                    
                                 model_type.extend(loc_tables[j].iloc[:,3].unique())

                    
                    
                    dict = {'city': city, 'no_router': no_router, 'city table': table }
                    dict_list.append(dict)
               
                         
        else:
            dict_list =[]
            model_class=[]
            model_type=[]
            mc_data = []
            table = None
            #for setting the router no. when the location is not inputted
            for i in range(len(location)):
                    city= location[i]

                    
                    if i == 0 and selected_sheet not in strn:
                        no_router= loc_tables[i].shape[0]-1
                        loc_tables[i]=loc_tables[i].iloc[1:,:]
                    else:
                        no_router= loc_tables[i].shape[0]

                   
                    # temptab= loc_tables[i].dropna() 
                    temptab= loc_tables[i]
                     
                    table = temptab.to_html(classes = 'data-table',index = False)
                 
                    model_class.extend(loc_tables[i].iloc[:,2].unique())
                    model_type.extend(loc_tables[i].iloc[:,3].unique())

                    #filtering condition   
                    if selected_model_class and not selected_model_type: 
                       

                        for mc in selected_model_class:
                            temp= loc_tables[i][(loc_tables[i].iloc[:,2]==mc)]
                             
                            mt= temp.iloc[:,3].unique()
                             
                            for t in mt:                                
                                tf = temp[temp.iloc[:,3]==t]                                                               
                                num= tf.shape[0]
                                tb= tf.to_html(classes = 'data-table',index = False)
                                mc_data.append({'city':city,'class':mc, 'type':t, 'num':num, 'tb':tb})







                        loc_tables[i]= loc_tables[i][(loc_tables[i].iloc[:,2].isin(selected_model_class))]
                        table = loc_tables[i].to_html(classes = 'data-table',index = False)
                        no_router = loc_tables[i].shape[0] 
                        model_type=[]                      
                        for j in range(len(location)):
                                model_type.extend(loc_tables[j].iloc[:,3].unique())                              
                     
                     

                    elif selected_model_type and not selected_model_class: 

                        for t in selected_model_type:
                            temp= loc_tables[i][(loc_tables[i].iloc[:,3]==t)]
                             
                            m= temp.iloc[:,2].unique()

                            for mc in m:                                
                                tf = temp[temp.iloc[:,2]==mc]                                
                                num= tf.shape[0]
                                tb= tf.to_html(classes = 'data-table',index = False)
                                mc_data.append({'city':city,'class':mc, 'type':t, 'num':num, 'tb':tb})





                        loc_tables[i]= loc_tables[i][(loc_tables[i].iloc[:,3].isin(selected_model_type))]
                        table = loc_tables[i].to_html(classes = 'data-table',index = False)
                        no_router = loc_tables[i].shape[0]  
                        model_class=[]
                        for j in range(len(location)):
                              model_class.extend(loc_tables[j].iloc[:,2].unique()) 

                    elif selected_model_type and selected_model_class: 

                        temp= loc_tables[i][(loc_tables[i].iloc[:,2].isin(selected_model_class))&(loc_tables[i].iloc[:,3].isin(selected_model_type))]
                        
                        m= temp.iloc[:,2].unique()
                        
                        for mc in m:
                            tf= temp[temp.iloc[:,2]==mc]
                            mt= tf.iloc[:,3].unique()
                            
                            for t in mt:                                
                                tf = temp[temp.iloc[:,3]==t]                                
                                
                                num= tf.shape[0]
                                tb= tf.to_html(classes = 'data-table',index = False)
                                mc_data.append({'city':city,'class':mc, 'type':t, 'num':num, 'tb':tb})




                        
                        loc_tables[i]= loc_tables[i][(loc_tables[i].iloc[:,2].isin(selected_model_class))]
                        temp2= loc_tables[i][(loc_tables[i].iloc[:,2].isin(selected_model_class))&(loc_tables[i].iloc[:,3].isin(selected_model_type))]
                        table =  temp2.to_html(classes = 'data-table',index = False)
                        no_router = temp2.shape[0]                        

                        model_type=[]   
                        for j in range(len(location)):
                            # print(location[j])
                            model_type.extend(loc_tables[j].iloc[:,3].unique()) 
                        
                        

                    
                    dict = {'city': city, 'no_router': no_router, 'city table': table}
                    dict_list.append(dict)
 
        
        
      



#some of the model classes and type are also 'nan' for some reason, we are not displaying those options in the filtering menu

        model_class = [x for x in model_class if str(x) != 'nan']                                  
        model_class= list(set(model_class))
         
            

        model_type = [x for x in model_type if str(x) != 'nan']                                  
        model_type= list(set(model_type))
        
#counting the number of routers in dict_list after all the filterings.
        if mc_data:
                       
            c_count= {}
            
            for data in mc_data:
                c = data['city']
                n = data ['num']
                c_count[c] =c_count.get(c, 0)+ n

            for data in dict_list:
                cn= data['city']
                data['no_router']= c_count.get(cn,0)
            
            
            
#counting the total number of routers in the dict_list            
        tot_router = 0       

        for dict in dict_list:
         tot_router= tot_router + dict['no_router']    

             

              
                    

           


 
    #tdata: a dictionary that has all the parameters and the filtering data that are needed to be shown in the flask web application.
  
    tdata = { 'sheet_names':sheet_names, #shows all the sheets available in the uploaded the excel file
               
              'selected_sheet': selected_sheet, #sets and shows the selected sheet in the filtering form

              'location': location, #shows the available location in the selected sheet
              'selected_location':selected_location, #sets and shows the selected location in the selected sheet
              

              'model_class':model_class, #shows the model class in the filtering form
              'selected_model_class':selected_model_class, #sets and shows the already selected model class in the filtering form

              'model_type': model_type, #shows the model types in the filtering form
              'selected_model_type':selected_model_type, #sets and shows the already selected model type in the filtering form

               'mc_data':mc_data, #to access the finer details of the table, or splitting the tables in even more parts we can print the mc_data in the webpage, {{right now it's not being used in the application, it's here for future use cases.}}

               'dict_list':dict_list, #displays the location, number of routers, and the table corresponding to the location 
               'tot_router':tot_router, # show the arithmatic sum of the number of routers in the dict_list 

               'no_filter_dict_list': no_filter_dict_list
               }
         
    return render_template('index.html', **tdata, file_path=file_path)

 
         
         
        
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

 
    
