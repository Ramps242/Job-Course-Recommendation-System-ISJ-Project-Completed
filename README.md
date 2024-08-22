# Job-Course-Recommendation-System-ISJ-Project
It's essentially a job recommendation system for the tech industry that utilizes datasets from Kaggle and employs machine learning algorithms to train the model.

#1.DIAGNOSE PROBLEM
The problem domain focuses on the gap between academic qualification, technical skills, and job market readiness for graduates in South Africa, specifically in the ICT field. Many of these graduates lack sufficient knowledge about the job market and struggle to find employment that matches their skills and qualifications. In the field of Information Commutation Technology it has be discovered that graduates who obtain the same qualification e.g. Computer Science qualification from the same institution may have varying skill sets.  These differences in skills can be explained by the knowledge and abilities that they acquire while still completing their undergraduate qualification and their involvement in work-integrated learning during their final year. As an illustration, ICT students at Tshwane University of Technology are obliged to complete practical training as part of graduation requirements.

This practical experience is typically gained from different organizations, exposing them to a range of technical skills. Moreover, individuals in the tech domain industry need to seek employment with specific skills they have obtained throughout their Work Integrated Learning programs.
 
The main issue is that most graduates are often lacking awareness of the specific job titles and also roles that are suitable for the skills that they have. They may also have a general idea of the industry they want to work in but they struggle to recognize the specific jobs that align with their skill sets that they have. As a result, they apply for positions that may not be the best fit for them, that will lead to a lack of success in their job hunting.

Another issue is that graduates are also unaware of the short courses that can enhance their employability. They may not know which expertise is in high demand in the job market or maybe which short certificate can help them to acquire those skills. Because they don't have enough information, they miss out on chances to learn new things and become experts in specific areas that would make them more appealing to employers.

#2.PROBLEM SOLUTION
To address the above issues, the proposed web app will leverage Natural Language Processing to analyze the resumes and extract essential detail such as skills. By using the information of skills that they obtained from Work Integrated Learning (WIL)/ internship practical experience, the system will provide personalized recommendations for suitable job titles and relevant online short courses certification using a random forest algorithm that will learn the patterns from the datasets that I will be using from Kaggle, with a help of collaborative filtering technique approach. 


 **Following The steps to utilize the recommendation system**
 1. Download the dataset from Kaggle named " jobs_dataset_with_features", cause I could not upload it. It was too large for Git
 2. Other datasets are uploaded make use of them
 3. Re-run all the models and save the model as an extension of .pkl( make sure dataset readers are on the same path)
 4. Install the kernel Python packages for models
 5. install streamlit packages
 6. Run "streamlit run App.py"


                    Designed by Christopher Thabo Rampora - School Research Project - ISJ117V


