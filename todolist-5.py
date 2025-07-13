from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen

import random
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://to-do-list-a6fe0-default-rtdb.firebaseio.com/'
})


# Dashboard Screen
def build_dashboard_screen(sm):
    screen = Screen(name='dashboard')
    layout = FloatLayout()

    # Title
    title = Label(text="[b]TO-DO LIST APP[/b]", markup=True,
                  font_size=24, size_hint=(1, 0.1),
                  pos_hint={'center_x': 0.5, 'top': 1})
    layout.add_widget(title)

    # Date
    today = datetime.now().strftime("%A, %d %B %Y")
    date_label = Label(text=f"[b]{today}[/b]", markup=True,
                       size_hint=(1, 0.05), pos_hint={'center_x': 0.5, 'top': 0.93},
                       color=(1, 1, 0, 1))
    layout.add_widget(date_label)

    # Task table
    table = GridLayout(cols=3, spacing=5, size_hint_y=None, padding=10)
    table.bind(minimum_height=table.setter('height'))

    scroll = ScrollView(size_hint=(1, 0.65), pos_hint={'x': 0, 'y': 0.25})
    scroll.add_widget(table)
    layout.add_widget(scroll)

    def load_dashboard(*args):
        table.clear_widgets()
        headers = ['OBJECTIVE', 'DEADLINE', 'PRIORITY']
        for header in headers:
            table.add_widget(Label(text=f"[b]{header}[/b]", markup=True, size_hint_y=None, height=40))

        tasks_ref = db.reference('tasks')
        tasks = tasks_ref.get()

        if tasks:
            for task_id, task in tasks.items():
                objective_text = task.get('objective', '')
                deadline_text = task.get('deadline', '')
                priority_text = task.get('priority', '')

                table.add_widget(Label(text=objective_text, markup=True, size_hint_y=None, height=40))
                table.add_widget(Label(text=deadline_text, markup=True, size_hint_y=None, height=40))
                table.add_widget(Label(text=priority_text, markup=True, size_hint_y=None, height=40))

    screen.bind(on_pre_enter=load_dashboard)

    # Add Task Button
    add_btn = Button(text="Add Task", size_hint=(0.3, 0.1), pos_hint={'center_x': 0.5, 'y': 0.05})
    add_btn.bind(on_press=lambda x: setattr(sm, 'current', 'add_task'))
    layout.add_widget(add_btn)

    # Refer Button to clear database
    refer_btn = Button(text="Clear Tasks", size_hint=(0.3, 0.1), pos_hint={'center_x': 0.5, 'y': 0.16})
    layout.add_widget(refer_btn)

    def clear_database(instance):
        db.reference('tasks').delete()
        table.clear_widgets()

    refer_btn.bind(on_press=clear_database)

    screen.add_widget(layout)
    return screen


# Add Task Screen
def build_add_task_screen(sm):
    screen = Screen(name='add_task')
    layout = FloatLayout()

    # Title
    title = Label(text="[b]ADD NEW TASK[/b]", markup=True,
                  font_size=24, size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'top': 1})
    layout.add_widget(title)

    # Objective
    layout.add_widget(Label(text="Objective", size_hint=(0.3, 0.08), pos_hint={'x': 0.05, 'top': 0.85}))
    obj_input = TextInput(size_hint=(0.6, 0.08), pos_hint={'x': 0.35, 'top': 0.85})
    layout.add_widget(obj_input)

    # Deadline
    layout.add_widget(Label(text="Deadline", size_hint=(0.3, 0.08), pos_hint={'x': 0.05, 'top': 0.7}))
    deadline_input = TextInput(hint_text="24H FORMAT", size_hint=(0.6, 0.08), pos_hint={'x': 0.35, 'top': 0.7})
    layout.add_widget(deadline_input)

    # Priority
    layout.add_widget(Label(text="Priority", size_hint=(0.3, 0.08), pos_hint={'x': 0.05, 'top': 0.55}))
    priority_input = Spinner(
        text='Select Priority',
        values=('High', 'Medium', 'Low'),
        size_hint=(0.6, 0.08),
        pos_hint={'x': 0.35, 'top': 0.55}
    )
    layout.add_widget(priority_input)

    # Save Button
    save_btn = Button(text="Save Task", size_hint=(0.3, 0.1), pos_hint={'center_x': 0.7, 'y': 0.05})
    layout.add_widget(save_btn)

    # Back Button
    back_btn = Button(text="Back", size_hint=(0.3, 0.1), pos_hint={'x': 0.2, 'y': 0.05})
    layout.add_widget(back_btn)
    back_btn.bind(on_press=lambda x: setattr(sm, 'current', 'dashboard'))

    def save_task(instance):
        objective = obj_input.text.strip()
        deadline = deadline_input.text.strip()
        priority = priority_input.text.strip()

        if objective:
            task_data = {
                'objective': objective,
                'deadline': deadline,
                'priority': priority,
                'done': False
            }
            task_id = f"task_{random.randint(1000, 9999)}"
            db.reference(f'tasks/{task_id}').set(task_data)

            obj_input.text = ""
            deadline_input.text = ""
            priority_input.text = "Select Priority"

            sm.current = 'dashboard'

    save_btn.bind(on_press=save_task)

    screen.add_widget(layout)
    return screen


# Build App
def build():
    sm = ScreenManager()
    sm.add_widget(build_dashboard_screen(sm))
    sm.add_widget(build_add_task_screen(sm))
    return sm


class MyApp(App):
    def build(self):
        return build()


if __name__ == "__main__":
    MyApp().run()
