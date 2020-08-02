from kivy.network.urlrequest import UrlRequest
from kivy.app import App
import certifi
import requests
import json


class MyFirebase():
    wak = "AIzaSyAMkaCGRT-xENBsw2cLvpDogGvaoRpnm88" #WEP API KEY

    def sign_up(self,email,password):
        app = App.get_running_app()
        email = email.replace("\n", "")
        password = password.replace("\n", "")
        # Send email and password to Firebase
        # Firebase will return localId, authToken (idToken), refreshToken
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        sign_up_data = json.loads(sign_up_request.content.decode())
        print(sign_up_request.ok)
        print(sign_up_request.content.decode())

        if sign_up_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']


            with open("refresh_token.txt", "w") as f:
                f.write(refresh_token)
            app = App.get_running_app()

            # Save LocalID in app
            app.local_id = localId
            app.id_Token = idToken






            #git ID

            friend_get_req = requests.get("https://al7amdolelah-bbff7.firebaseio.com/next_friend_id.json?auth=" + idToken)
            print("friends",friend_get_req.json())
            #SAVE MY ID

            my_friend_id = friend_get_req.json()
            print("IDDDD",my_friend_id)

            #CHANGE NEXT ID

            friend_patch_data = '{"next_friend_id":%s}'% str(my_friend_id+1)
            friend_patch_req = requests.patch("https://al7amdolelah-bbff7.firebaseio.com/.json?auth="+idToken ,data=friend_patch_data)

            # TEST
            print("okokokokko")

            # Default avatar

            my_data = '{"avatar": "girl.png","friends":"","workouts":"","streak": "22","my_friend_id":%s}' % my_friend_id

            # New data in firebase
            post_requests = requests.patch( "https://al7amdolelah-bbff7.firebaseio.com/" + localId + ".json?auth=" + idToken, data=my_data)
            print(post_requests)
            print(json.loads(post_requests.content.decode()))


            print(my_data)

            app.change_screen("home_screen")
        if sign_up_request.ok == False:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data["error"]['message']


            app.root.ids['login_screen'].ids['login_message'].text = error_message

        pass

    def on_friend_get_req_ok(self, *args):
        app = App.get_running_app()
        my_friend_id = self.friend_get_req.json()
        app.set_friend_id(my_friend_id)
        friend_patch_data = '{"next_friend_id": %s}' % (my_friend_id+1)
        friend_patch_req = UrlRequest("https://al7amdolelah-bbff7.firebaseio.com/.json?auth=" + app.id_token,
                                          req_body=friend_patch_data, ca_file = certifi.where(), method='PATCH')


        # Update firebase's next friend id field
        # Default streak
        # Default avata
        # Friends list
        # Empty workouts area
        my_data = '{"avatar": "man.png", "nicknames": {}, "friends": "", "workouts": "", "streak": "0", "my_friend_id": %s}' % my_friend_id
        post_request = UrlRequest("https://al7amdolelah-bbff7.firebaseio.com/" + app.local_id + ".json?auth=" + app.id_token, ca_file=certifi.where(),
                       req_body=my_data, method='PATCH')

        app.change_screen("home_screen")
    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.wak
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)
        id_token = refresh_req.json()['id_token']
        local_id = refresh_req.json()['user_id']
        return id_token, local_id

    def sin_in(self):
        pass