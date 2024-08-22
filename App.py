import streamlit as st
import nltk
import spacy

nltk.download('stopwords')
spacy.load('en_core_web_sm')

import pandas as pd
import base64, random
import time, datetime
from pytube import YouTube
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io, random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
import pafy
import plotly.express as px
import nltk
import matplotlib.pyplot as plt
import re
import pickle
import warnings
import mysql.connector
from time import sleep
warnings.filterwarnings('ignore')


def fetch_yt_video(link):  #Accessing youtube videos function
    video = pafy.new(link)
    return video.title


def get_table_download_link(df, filename, text):  #Setting a report 
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):  #Resume reader function
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    #close open handles
    converter.close()
    fake_file_handle.close()
    return text

         #===================Function for upload=========== 
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
   
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


connection = pymysql.connect(host='localhost', user='root', password='')   #Connecting a database
cursor = connection.cursor()

  #==============================Coloumn names database=============================
def insert_data(name, email, contactNo, timestamp, reco_job_category,  reco_job_title, skills):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = ( name, email,contactNo, timestamp, reco_job_category,reco_job_title, skills)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

#======================================System name and center the display view===============================
def set_page_config():
    st.set_page_config(
        page_title="ISJ_System",
        layout='centered'
    )
set_page_config()


#============================================IMPORTED MODELS FOR JOB TITLES================================================
rf_classifier_categorization = pickle.load(open(r'C:\ISJ PROJECT\ISJ_Resume_Analyser\model\rf_classifier_categorization.pkl', 'rb'))
tfidf_vectorizer_categorization = pickle.load(open(r'C:\ISJ PROJECT\ISJ_Resume_Analyser\model\tfidf_vectorizer_categorization.pkl', 'rb'))
rf_classifier_job_recommendation = pickle.load(open(r'C:\ISJ PROJECT\ISJ_Resume_Analyser\model\rf_classifier_job_recommendation.pkl', 'rb'))
tfidf_vectorizer_job_recommendation = pickle.load(open(r'C:\ISJ PROJECT\ISJ_Resume_Analyser\model\tfidf_vectorizer_job_recommendation.pkl', 'rb'))

#============================================IMPORTED MODELS FOR SHORT COURSES================================================
courses_list = pickle.load(open(r'C:\ISJ PROJECT\ISJ_Resume_Analyser\courses.pkl','rb'))
similarity = pickle.load(open(r'C:\ISJ PROJECT\ISJ_Resume_Analyser\similarity.pkl','rb'))

#============================================Adding icons==================================================
st.markdown('<script src="https://kit.fontawesome.com/2c74303849.js" crossorigin="anonymous"></script>', unsafe_allow_html=True)


def run():
    activities = ["Normal User", "Admin","Find Short Courses" ,"About"] # Setting the options to page access
    choice = st.sidebar.selectbox("**Choose among the given options:**", activities)   #Drop down optiions
    img = Image.open('./Logo/logo1.png')
    img = img.resize((1280, 500))
   
    # Creating the Database
    db_sql = """CREATE DATABASE IF NOT EXISTS jobskill_flow;""" 
    cursor.execute(db_sql)
    connection.select_db("sra")   #Database name

    # Creating the  table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(100) NOT NULL,
                     Email_ID VARCHAR(50) NOT NULL,
                     Contact VARCHAR(15) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Predicted_Job_Category VARCHAR(300) NOT NULL,
                     Recommended_Job_Title VARCHAR(300) NOT NULL,
                     UsersSkills VARCHAR(300) NOT NULL,
                     PRIMARY KEY (ID));
                      """
    cursor.execute(table_sql) #Executing the table from the database
   
                           #===================================Options for user type==============================
    if choice == 'Normal User':
        st.markdown('<p style="color: lime;text-shadow: 4px 4/,px 5px #0000FF ;font-size: 45px; font-weight: bold; text-align: center; font-style: italic;">WELCOME</p>', unsafe_allow_html=True)
        st.markdown('<p style="color: lime;text-shadow: 4px 4/,px 5px #0000FF ;font-size: 45px; font-weight: bold; text-align: center; font-style: italic;">TO </p>', unsafe_allow_html=True)
        st.image(img)    
         
        st.sidebar.image("./Logo/man.png", width = 270)
        pdf_file = st.file_uploader("**Choose your Resume**", type=["pdf"])  #Only pdf can be uploaded restrictions
        progress = st.sidebar.progress(5)   ##Normal User loading side 
        for i in range(100):
         progress.progress(i + 1)     
            
        if pdf_file is not None:  #Checking if there is a pdf file  (only pdf's are being accepted)
         with st.spinner('Uploading your Resume....'):
            time.sleep(3)
            st.success('**After uploading your resume, please wait few seconds while its extracing...**', icon ="✅")
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()  #Extracting  resume data using AI libraries imported and store it in reusme_data viriable
                         
                    #====================Extracting whole resume data========================================
            if resume_data:
                ## Getting the whole resume data
                resume_text = pdf_reader(save_image_path)
                st.write('')
                st.write('')
                st.markdown("<h1 style='color:white ;text-align: center; padding: 8px; font-weight: bold;'><svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-info'><circle cx='12' cy='12' r='10'></circle><line x1='12' y1='16' x2='12' y2='12'></line><line x1='12' y1='8' x2='12' y2='8'></line></svg> Your basic information </h1>", unsafe_allow_html=True)
                st.success("Hello " + resume_data['name'])                
                try:
                         #================================Displaying the extracted data to show the Natural Language processing if it does works==================
                    name = resume_data['name']
                    name_init_cap = name.title()  #Turning the name to initcap just incase the name is in capital letters
                    st.text('Name: ' + name_init_cap)
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                 
                except:
                    pass               
                st.markdown("<h3 style='color: lightgreen;text-align: center; font-weight: bold;'>Skills that you have </h3>", unsafe_allow_html=True)

                   #==============================Skills extracted from the user resume================================
                resumeSkills = st_tags(label='',text='**See skills extracted from your resume**',  value=resume_data['skills'], key='1')
                 
                    #=========================================Resume Cleaning (Data Pre-processing)=================================================
                def cleanResume(txt):
                    cleanText = re.sub('http\S+\s', ' ', txt)
                    cleanText = re.sub('RT|cc', ' ', cleanText)
                    cleanText = re.sub('#\S+\s', ' ', cleanText)
                    cleanText = re.sub('@\S+', '  ', cleanText)
                    cleanText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', cleanText)
                    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)
                    cleanText = re.sub('\s+', ' ', cleanText)
                    return cleanText

                #Job Category Recommendation
                def predict_category(resume_text):
                    resume_text = cleanResume(resume_text)
                    resume_tfidf = tfidf_vectorizer_categorization.transform([resume_text])
                    predicted_category = rf_classifier_categorization.predict(resume_tfidf)[0]
                    return predicted_category

                # Job title recommendation
                def job_recommendation(resume_text):
                    resume_text= cleanResume(resume_text)
                    resume_tfidf = tfidf_vectorizer_job_recommendation.transform([resume_text])
                    recommended_job = rf_classifier_job_recommendation.predict(resume_tfidf)[0]
                    return recommended_job
                

                predicted_category = predict_category(resume_text)   #Job category Reccommedation display
                recommended_job = job_recommendation(resume_text)    #Job title recommendation that coresspond with a job category display
                
              
                #Reccomendation results based on the trained model
                st.markdown("<h3 style='color: lightgreen;text-align: center; padding: 8px; font-weight: bold;'>Categorization Prediction & Job Recommendation👨‍💼 </h3>", unsafe_allow_html=True)
                
                predicted_category_initcap = predicted_category.title()
                recommended_job_initcap = recommended_job.title()
                
                #Category
                st.success("Based on your resume, the following prediction job category falls under :" )
                st.markdown(f"<div style='background-color: darkgreen; padding: 10px;  text-align:center; border-radius: 10px;'><h3> <span style='color: lightyellow;'>{predicted_category_initcap}</span></h3></div>", unsafe_allow_html=True)
                  
                
                #Job title recommendation
                st.text('')
                st.success("Based on your resume, the following job recommendation title is :" )
                st.markdown(f"<div style='background-color: darkgreen; padding: 10px;  text-align:center; border-radius: 10px;'><h3> <span style='color: lightyellow;'>{recommended_job_initcap}</span></h3></div>", unsafe_allow_html=True)
                  
                st.text('')
                st.text('')
                st.markdown("<h3 style='color: lightgreen;text-align: center; padding: 8px; font-weight: bold;'>✅Bonus video for Resume Writing tips 💡</h3>", unsafe_allow_html=True)
  
            def fetch_yt_video_title(video_url): #Fecthing Videos Randomly
                try:
                   yt = YouTube(video_url)
                   return yt.title
                except:
                   return "Video Title Not Found"
               
                  #===========================Random Youtube Videos for additional tip on how to pass and interview and also on how to tailor a resume for ATS===============
            resume_videos = ['https://youtu.be/y8YH0Qbu5h4','https://youtu.be/J-4Fv8nq1iA',
                 'https://youtu.be/yp693O87GmM','https://youtu.be/UeMmCex9uTU',
                 'https://www.youtube.com/watch?v=Tt08KmFfIYQ','https://youtu.be/HQqqQx5BCFY',
                 'https://youtu.be/CLUsplI4xMU','https://youtu.be/pbczsLkv7Cc',
                 'https://www.youtube.com/watch?v=fHpVPkIGVyY','https://www.youtube.com/watch?v=JG_kC5Iwo5M'
                 'https://www.youtube.com/watch?v=JE_EzNK56gQ&t=431s','https://www.youtube.com/watch?v=DksA_vF84JA',
                 'https://www.youtube.com/watch?v=pjqi_M3SPwY','https://www.youtube.com/watch?v=7apj4sVvbro'
                 'https://www.youtube.com/watch?v=SChM-Nd7XNo','https://www.youtube.com/watch?v=3agP4x8LYFM&t=15s']


            interview_videos = ['https://www.youtube.com/watch?v=XJICiQPjSfw','https://www.youtube.com/watch?v=HG68Ymazo18',
                    'https://www.youtube.com/watch?v=-snw_gwviHY','https://www.youtube.com/watch?v=5v-wyR5emRw',
                    'https://www.youtube.com/watch?v=wBJ0MUkA1cA','https://www.youtube.com/watch?v=UUWBpHA0M7w&t=83s'
                    'https://www.youtube.com/watch?v=KukmClH1KoA','https://www.youtube.com/watch?v=PCWVi5pAa30',
                    'https://www.youtube.com/watch?v=CAr7qzzZWZE','https://www.youtube.com/watch?v=cm8cpn1lR6c',
                    'https://www.youtube.com/watch?v=ZdjJdoEwCY4','https://www.youtube.com/watch?v=NA5_WyR6xYM'
                    'https://www.youtube.com/watch?v=TQHW7gGjrCQ','https://www.youtube.com/watch?v=TZ3C_syg9Ow',
                    'https://www.youtube.com/watch?v=1mHjMNZZvFo','https://www.youtube.com/watch?v=e733E9156xA']

              #==================Extracting title of the videos for user displayment======================
            resume_vid = random.choice(resume_videos)
            res_vid_title = fetch_yt_video_title(resume_vid)
            st.subheader(" *🔊*" + res_vid_title + "**")

            st.text('')
            st.markdown("<h3 style='color: lightgreen;text-align: center; padding: 8px; font-weight: bold;'>✅Bonus Video for Interview Preparation Tips 💡</h3>", unsafe_allow_html=True)
            interview_vid = random.choice(interview_videos)
            int_vid_title = fetch_yt_video_title(interview_vid)
            st.video(resume_vid)
            st.subheader(" *🔊*" + int_vid_title + "**")
            st.video(interview_vid)
            
            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            timestamp = str(cur_date + '_' + cur_time)
                      
            insert_data(str(resume_data['name']),str(resume_data['email']),str(resume_data['mobile_number']), timestamp,
                        str( predicted_category_initcap), str(recommended_job_initcap), str(resume_data['skills']))

            connection.commit()
            st.balloons()
        else:    
              #=================================Function for system real time clock=====================
            clock_container = st.empty()
            def update_clock():
               current_time = time.strftime("%H:%M:%S")
               clock_container.markdown(f"<h1 style='text-align: center; color:lime;'>{current_time}</h1>", unsafe_allow_html=True)

            while True:
                    update_clock()
                    time.sleep(1)
 
       #=====================================Admin Side Tab===================================
    elif choice == 'Admin':
        st.image(img)
        st.success('Welcome to Admin Side')
        st.sidebar.image("./Logo/admin-panel.png", width=270)
        progress = st.sidebar.progress(1000) 
        
        ad_user = st.text_input("**Username**")       
        ad_password = st.text_input("**Password**", type='password')
        if st.button('Login'):
            if ad_user == 'CT Rampora' and ad_password == '@Thabo242.**':  # Credentials of the admin 
                st.markdown("<h1 style='color: lime;text-align: center; font-weight: bold;'>Welcome Administrator 👨‍💻 </h1>", unsafe_allow_html=True)
                
                # Display resume data 
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()  #Fetching the data
                st.markdown('<p style="color: white; font-size: 45px; font-weight: bold; text-align: center; font-style: italic;"> All Resume Data</p>', unsafe_allow_html=True)
                        #=======================Storing data into coloumns========================
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Contact','Timestamp',
                                                'Predicted_Job_Category', 'Recommended_Job_Title', 
                                                'UsersSkills'])
                st.dataframe(df)
                 #====================Link to download data in a csv format===============================
                st.markdown('<center><button style="background-color: lime;">' + get_table_download_link(df, 'User_Data.csv', ' DOWNLOAD ALL RESUME REPORT') + '</button></center>', unsafe_allow_html=True)
             
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection) #Retrieving data from database to plot the pie chart
                values = plot_data['Predicted_Job_Category'].value_counts().values  
                labels = plot_data['Predicted_Job_Category'].value_counts().index
            
                # =====================================Create the pie chart for exploritory data =====================
                plt.pie(values, labels=labels, autopct='%1.1f%%')  #Setting the labels and values for pie charts
                st.write('')
                st.markdown("<h1 style='color: lime;text-align: center; font-weight: bold;'>⚖️ Exploratory Data Analysis ⚖️ </h1>", unsafe_allow_html=True)
                st.write('')
                st.markdown("<h3 style='color: lightgreen;text-align: center; font-weight: bold;'>🔍Pie-Chart for Job category Recommendations</h3>", unsafe_allow_html=True)
                
                fig = px.pie(df, values=values, names=labels, title='Recommended job categories according to the users skills')
                st.plotly_chart(fig)   #Plotting
                
    
                values = plot_data['Recommended_Job_Title'].value_counts().values
                labels = plot_data['Recommended_Job_Title'].value_counts().index
                st.markdown("<h3 style='color: lightgreen;text-align: center; font-weight: bold;'>🔍Pie-Chart for Job Title Recommendations</h3>", unsafe_allow_html=True)
                fig = px.pie(df, values=values, names=labels, title="Recommendeded job titles according to the users skills")
                st.plotly_chart(fig)  #Plotting
                
                st.balloons()  #Loading balloons alert
                exit()
            else:
                   st.error("Incorrect username or password provided, please try again...") 
                   
                   #============================================About Side Tab=========================================================
    elif choice == 'About':    
         st.write('')
         st.sidebar.image("Logo/sign.png", width = 270)
         img = Image.open('Logo/Blue.png')
         img = img.resize((1150, 1750))
         st.image(img)    
         
         progress2 = st.sidebar.progress(5)  
         for i in range(100):
          progress2.progress(i + 1)       
          
                         #==========================================Course Recommendation Tab===========================================
    elif choice == "Find Short Courses":                    
            st.sidebar.image("Logo/book.png", width=250)
            progress = st.sidebar.progress(100)
            def recommend(course):
                index = courses_list[courses_list['course_name'] == course].index[0]
                distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])  
                
                #Declaring variables that will store 
                recommended_course_names = []
                formatted_recommendations = []  
                course_count = 1
                
                #==========================Loop structure that will loop throught the dataset of short courses============================
                for i in distances[1:7]:
                    course_name = courses_list.iloc[i[0]]['course_name']  #A list that store all recommended course names
                    course_url = courses_list.iloc[i[0]]['course_url']    #A list that store all recommended course links
                    recommended_course_names.append((course_name,course_url)) #Appending boths lists   
                    formatted_recommendations.append(f"✔️COURSE NO {course_count}: {course_name}\n COURSE LINK: 📗 {course_url} 📗") #Formatting since it has links  
                    
                    course_count += 1 #Increment the counter
                    
                return formatted_recommendations  
            
            st.markdown('<p style="color: lime;text-shadow: 4px 4/,px 5px #0000FF ;font-size: 45px; font-weight: bold; text-align: center;">Welcome To Coursera Free Short Courses Recommendation	💼</p>', unsafe_allow_html=True)
            st.success("Find similar short tech courses from a dataset of over 3,000 courses from Coursera!")
            
            course_list = courses_list['course_name'].values
            selected_course = st.selectbox(
                "Type or select a course you like :",
                course_list
            )
             #===========================Short Courses Recommendation based on the users input==========================
            if st.button('Show Recommended Courses'):
                st.write("Recommended short courses based on your interests are:")
                formatted_recommendations = recommend(selected_course)
                
                # Display up to 6 recommended courses
                for i in range(min(6, len(formatted_recommendations))):
                    st.text(formatted_recommendations[i])
                    
                st.text(" ")
                st.success('😀😀😀😀Copy "COURSE LINK" and paste it on the browser😀😀😀😀')  #Alerting message on instructions on how to access the course links
                st.markdown("<h5 style='text-align: center; color: red;'>Please visit Cousera website to complete courses recommended above!!!</h5>", unsafe_allow_html=True)
run()

