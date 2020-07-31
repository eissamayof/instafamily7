from os import walk
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen   ,  NoTransition, CardTransition
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from workoutbanner import WorkoutBanner
from functools import partial
from myfirebase import MyFirebase

import requests
import json


class HomeScreen(Screen):
    pass

class ChangeAvatarScreen(Screen):
    pass

class LoginScreen(Screen):
    pass

class FriendsListScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class AddFriendScreen(Screen):
    pass

class LabelButton(ButtonBehavior,Label):
    pass

class FriendWorkoutScreen(Screen):
    pass

class AddWorkoutScreen(Screen):
    pass

class ImageButton(ButtonBehavior,Image):
    pass


#GUI =   # Make sure this is after all class definitions!
GUI = Builder.load_file("main.kv")


# THE MAIN APP
class MainApp(App):
    my_friend_id = 1
    option_choice = None

    workout_image = None
    def build(self):
        self.my_firebase = MyFirebase()

        return GUI


    def update_workout_image(self,filename,widget_id):
        self.workout_image = filename

    def on_start(self):

        # changing avatars image
        avatar_grid = self.root.ids['change_avatar_screen'].ids['avatar_grid']
        for root_dir, folders, files in walk("icons/avatars"):
            for f in files:
                img = ImageButton(source="icons/avatars/" + f, on_release=partial(self.change_avatar, f))
                avatar_grid.add_widget(img)

        # WORKOUT GRID TO CHOSE IMAGE

        workout_image_grid = self.root.ids['add_workout_screen'].ids['workout_image_grid']
        for root_dir, folders, files in walk("icons/workouts"):
            for f in files:
                if '.png' in f:
                    img = ImageButton(source="icons/workouts/" + f, on_release=partial(self.update_workout_image,f))
                    workout_image_grid.add_widget(img)



        try:
            with open("refresh_token.txt","r") as f:
                refresh_token = f.read()

            id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

        #get database
            result = requests.get("https://al7amdolelah-bbff7.firebaseio.com/" +self.local_id + ".json?auth="+self.id_token)
            print("was do ok", result.ok)
            data = json.loads(result.content.decode())
            print(data)

        #
            self.my_friend_id = data['my_friend_id']
            friend_id_label = self.root.ids['settings_screen'].ids['friend_id_label']
            friend_id_label.text = "Friend ID: " + str(self.my_friend_id)
         #MAIN AVATAR
            avatar_image = self.root.ids['avatar_image']
            avatar_image.source = "icons/avatars/" + data['avatar']

        # GET FRIEND LIST
            self.friend_list = data['friends']

        # THE MAIN NUMBER

            streak_label = self.root.ids['home_screen'].ids['streak_label']
            streak_label.text = str(data['streak']) + "  Day streak"

# Ted Freind id
            friend_id_label = self.root.ids['settings_screen'].ids['friend_id_label']
            friend_id_label.text = str(data['my_friend_id']) + "  MY ID"





        # BANNER GRID FOR WORKOUTS


            banner_grid = self.root.ids['home_screen'].ids['banner_grid']

        # WORKOUTS

            workouts = data['workouts']
            workout_keys = workouts.keys()
            for workout_key in workout_keys:
                workout = workouts[workout_key]
                W = WorkoutBanner(workout_image=workout['workout_image'], description=workout['description'],
                                      type_image=workout['type_image'], number=workout['number'], units=workout['units'],
                                      likes=workout['likes'], date=workout['date'])
                banner_grid.add_widget(W)




            self.root.ids["screen_manager"].transition = NoTransition()
            self.change_screen("home_screen")
            self.root.ids["screen_manager"].transition = CardTransition()
        except Exception as e:

            pass

    def set_friend_id(self, my_friend_id):
        self.my_friend_id = my_friend_id
        friend_id_label = self.root.ids['settings_screen'].ids['friend_id_label']
        friend_id_label.text = "Friend ID: " + str(self.my_friend_id)


        #exchang user

    def add_friend(self, friend_id):
        friend_id = friend_id.replace("\n","")
        # Make sure friend id was a number otherwise it's invalid
        try:
            int_friend_id = int(friend_id)
        except:
            # Friend id had some letters in it when it should just be a number
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "Friend ID should be a number."
            return
        # Make sure they aren't adding themselves
        if friend_id == self.my_friend_id:
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "You can't add yourself as a friend."
            return

        # Make sure this is not someone already in their friends list




        # Query database and make sure friend_id exists
        check_req = requests.get('https://al7amdolelah-bbff7.firebaseio.com/.json?orderBy="my_friend_id"&equalTo=' + friend_id)
        data = check_req.json()
        print(check_req.ok)
        print("hahaeeeee",check_req.json())
        print("friend id", friend_id)

        if data == {}:
            # If it doesn't, display it doesn't in the message on the add friend screen
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "Invalid friend ID"
        else:
            key = list(data.keys())[0]
            new_friend_id = data[key]['my_friend_id']
            print("new friend id ",new_friend_id)
            self.root.ids['add_friend_screen'].ids['add_friend_label'].text = "FRIEND ID %s ADDED SUCCSEES" % friend_id

   # ADD NEW FRIEND ID TO MY LIST FRIEND
            self.friend_list += ", %s" %friend_id
            patch_data = '{"friends": "%s"}'%self.friend_list
            patch_req = requests.patch("https://al7amdolelah-bbff7.firebaseio.com/%s.json?auth=%s"%(self.local_id, self.id_token ), data=patch_data)
            print("gooooooooool",patch_req.ok)
            print(patch_req.json())


    #ADD WORKOUT
    def add_workout(self):
        # Get data from all fields in add workout screen
        workout_ids = self.root.ids['add_workout_screen'].ids

        workout_image_grid = self.root.ids['add_workout_screen'].ids['workout_image_grid']


        # Already have workout image in self.workout_image variable
        description_input = workout_ids['description_input'].text
        # Already have option choice in self.option_choice
        quantity_input = workout_ids['quantity_input'].text
        units_input = workout_ids['units_input'].text
        month_input = workout_ids['month_input'].text
        day_input = workout_ids['day_input'].text
        year_input = workout_ids['year_input'].text

        # Make sure fields aren't garbage
        if self.workout_image == None:
            print("MAY BE ES")
            return
        # They are allowed to leave no description
        if self.option_choice == None:
            workout_ids['time_label'].color = (1,0,0,1)
            workout_ids['distance_label'].color = (1,0,0,1)
            workout_ids['sets_label'].color = (1,0,0,1)
            return
        try:
            int_quantity = float(quantity_input)
        except:
            workout_ids['quantity_input'].background_color = (1,0,0,1)
            return
        if units_input == "":
            print("goood jop")
            workout_ids['units_input'].background_color = (1,0,0,1)
            return
        try:
            int_month = int(month_input)
            if int_month > 12:
                workout_ids['month_input'].background_color = (1, 0, 0, 1)
                return
        except:
            workout_ids['month_input'].background_color = (1,0,0,1)
            return
        try:
            int_day = int(day_input)
            if int_day > 31:
                workout_ids['day_input'].background_color = (1, 0, 0, 1)
                return
        except:
            workout_ids['day_input'].background_color = (1,0,0,1)
            return
        try:
            if len(year_input) == 2:
                year_input = '20'+year_input
            int_year = int(year_input)
        except:
            workout_ids['year_input'].background_color = (1,0,0,1)
            return

        # If all data is ok, send the data to firebase real-time database
        workout_payload = {"workout_image": self.workout_image, "description": description_input, "likes": 0,
                           "number": float(quantity_input), "type_image": self.option_choice, "units": units_input,
                           "date": month_input + "/" + day_input + "/" + year_input}
        workout_request = requests.post("https://al7amdolelah-bbff7.firebaseio.com/%s/workouts.json?auth=%s"
                                        %(self.local_id, self.id_token), data=json.dumps(workout_payload))
        print(workout_request.json())
    #  changing avatars image

    def change_avatar(self,Image,Widget):
        #change avatar in app
        avatar_image = self.root.ids["avatar_image"]
        avatar_image.source = 'icons/avatars/'+ Image
      #change avatar in fire base
        my_data = '{"avatar": "%s"}' % Image
        print(my_data)
        requests.patch("https://al7amdolelah-bbff7.firebaseio.com/%s.json?auth=%s" %(self.local_id, self.id_token), data=my_data)
        self.change_screen("settings_screen")
        pass




















     # CHANGE SCREEN
    def change_screen(self, screen_name):
        # Get the screen manager from the kv file

        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name





my_app = MainApp()
my_app.run()





