pip install -r requirements.txt

# Modules
import pyrebase
import streamlit as st
from datetime import datetime

import streamlit as st

def app():
    st.set_page_config(page_title="Marine Life", page_icon=":fish:", layout="wide")

    # Add background image to the login page
    login_bg_img = '''
    <style>
    body {
    background-image: url("https://live.staticflickr.com/65535/52773993547_f7f34867b9_k.jpg");
    background-size: cover;
    background-position: center;
    }
    .login-text {
    font-size: 48px;
    font-weight: bold;
    color: lightblue;
    text-shadow: 2px 2px #0000FF;
    }
    </style>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet">

    '''
    st.markdown(login_bg_img, unsafe_allow_html=True)

    # Add text and logo to the login page
    st.write("<div class='login-text'><i class='fas fa-fish'></i> Welcome to Marine Life!</div>", unsafe_allow_html=True)

    # Add text and images to the app
    st.title("Gis Mappers")
    st.write("Explore the beauty of marine life!")
    st.image("background.jpg", use_column_width=True)
    

if __name__ == '__main__':
    app()




# Configuration Key
firebaseConfig = {
  'apiKey': "AIzaSyD85kXIHta_Gn-sNoqp0kzkDklY6D1p8vU",
  'authDomain': "gis-mappers-web-app.firebaseapp.com",
  'projectId': "gis-mappers-web-app",
  'databaseURL': "https://gis-mappers-web-app-default-rtdb.europe-west1.firebasedatabase.app/",
  'storageBucket': "gis-mappers-web-app.appspot.com",
  'messagingSenderId': "1058920095566",
  'appId': "1:1058920095566:web:113e7af0c16333ff5b481f",
  'measurementId': "G-4RFCJFDNJN"
}


# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Database
db = firebase.database()
storage = firebase.storage()
st.sidebar.title("Gis Mappers")

# Authentication
choice = st.sidebar.selectbox('login/Signup', ['Login', 'Sign up'])

# Obtain User Input for email and password
email = st.sidebar.text_input('Please enter your email address')
password = st.sidebar.text_input('Please enter your password',type = 'password')

# App 

import streamlit as st



# Sign up Block
if choice == 'Sign up':
    handle = st.sidebar.text_input(
        'Please input your app handle name', value='Default')
    submit = st.sidebar.button('Create my account')

    if submit:
        user = auth.create_user_with_email_and_password(email, password)
        st.success('Your account is created suceesfully!')
        st.balloons()
        # Sign in
        user = auth.sign_in_with_email_and_password(email, password)
        db.child(user['localId']).child("Handle").set(handle)
        db.child(user['localId']).child("ID").set(user['localId'])
        st.title('Welcome' + handle)
        st.info('Login via login drop down selection')

# Login Block
if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        user = auth.sign_in_with_email_and_password(email,password)
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        bio = st.radio('Jump to',['Home','Workplace Feeds', 'Upload Marine Data'])
        
# Upload Marine Data PAGE 
        if bio == 'Upload Marine Data':  
            # CHECK FOR IMAGE
            nImage = db.child(user['localId']).child("Image").get().val()    
            # IMAGE FOUND     
            if nImage is not None:
                # We plan to store all our image under the child image
                Image = db.child(user['localId']).child("Image").get()
                for img in Image.each():
                    img_choice = img.val()
                    #st.write(img_choice)
                st.image(img_choice)
                exp = st.expander('Change Bio and Image')  
                # User plan to change profile picture  
                with exp:
                    newImgPath = st.text_input('Enter full path of your profile imgae')
                    upload_new = st.button('Upload')
                    if upload_new:
                        uid = user['localId']
                        fireb_upload = storage.child(uid).put(newImgPath,user['idToken'])
                        a_imgdata_url = storage.child(uid).get_url(fireb_upload['downloadTokens']) 
                        db.child(user['localId']).child("Image").push(a_imgdata_url)
                        st.success('Success!')           
            # IF THERE IS NO IMAGE
            else:    
                st.info("No profile picture yet")
                newImgPath = st.text_input('Enter full path of your profile image')
                upload_new = st.button('Upload')
                if upload_new:
                    uid = user['localId']
                    # Stored Initated Bucket in Firebase
                    fireb_upload = storage.child(uid).put(newImgPath,user['idToken'])
                    # Get the url for easy access
                    a_imgdata_url = storage.child(uid).get_url(fireb_upload['downloadTokens']) 
                    # Put it in our real time database
                    db.child(user['localId']).child("Image").push(a_imgdata_url)
 # HOME PAGE
        elif bio == 'Home':
            col1, col2 = st.columns(2)
            
            # col for Profile picture
            with col1:
                nImage = db.child(user['localId']).child("Image").get().val()         
                if nImage is not None:
                    val = db.child(user['localId']).child("Image").get()
                    for img in val.each():
                        img_choice = img.val()
                    st.image(img_choice,use_column_width=True)
                else:
                    st.info("No profile picture yet. Go to Edit Profile and choose one!")
                
                post = st.text_input("Let's share my current mood as a post!",max_chars = 100)
                add_post = st.button('Share Posts')
            if add_post:   
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")              
                post = {'Post:' : post,
                        'Timestamp' : dt_string}                           
                results = db.child(user['localId']).child("Posts").push(post)
                st.snow()

            # This coloumn for the post Display
            with col2:
                
                all_posts = db.child(user['localId']).child("Posts").get()
                if all_posts.val() is not None:    
                    for Posts in reversed(all_posts.each()):
                            #st.write(Posts.key()) # Morty
                            st.code(Posts.val(),language = '') 
   # WORKPLACE FEED PAGE
        else:
            all_users = db.get()
            res = []
            # Store all the users handle name
            for users_handle in all_users.each():
                k = users_handle.val()["Handle"]
                res.append(k)
            # Total users
            nl = len(res)
            st.write('Total users here: '+ str(nl)) 
            
            # Allow the user to choose which other user he/she wants to see 
            choice = st.selectbox('My Collegues',res)
            push = st.button('Show Profile')
            
            # Show the choosen Profile
            if push:
                for users_handle in all_users.each():
                    k = users_handle.val()["Handle"]
                    # 
                    if k == choice:
                        lid = users_handle.val()["ID"]
                        
                        handlename = db.child(lid).child("Handle").get().val()             
                        
                        st.markdown(handlename, unsafe_allow_html=True)
                        
                        nImage = db.child(lid).child("Image").get().val()         
                        if nImage is not None:
                            val = db.child(lid).child("Image").get()
                            for img in val.each():
                                img_choice = img.val()
                                st.image(img_choice)
                        else:
                            st.info("No profile picture yet. Go to Edit Profile and choose one!")
 
                        # All posts
                        all_posts = db.child(lid).child("Posts").get()
                        if all_posts.val() is not None:    
                            for Posts in reversed(all_posts.each()):
                                st.code(Posts.val(),language = '')
