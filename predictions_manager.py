import tkinter as tk
import json


with open('predictions/predictions.json', 'r') as file:
    dict = json.load(file)


#TODO delete current, update listbox when saving and deleting
# side note: by changing the Name field you create a new prediction, if you only want to change the Name field don't forget to delete the old prediction with the old name


def handle_select_pred(event):
    selected_pred = lb_list.curselection()
    selected_pred_name = lb_list.get(selected_pred)

    ent_name.delete(0, tk.END)

    ent_splitname.delete(0, tk.END)
    auto_start.set(0)

    ent_title.delete(0, tk.END)
    for outcome in outcomes:
        outcome.delete(0, tk.END)

    ent_window.delete(0, tk.END)

    for pred in dict['predictions']:
        if pred['name'] == selected_pred_name:
            file_auto_start = pred['auto_predict']['auto_start']
            file_splitname = pred['auto_predict']['split_name']
            file_title = pred['data']['title']
            file_outcomes = pred['data']['outcomes']
            file_window = pred['data']['prediction_window']

            ent_name.insert(0, pred['name'])

            if file_auto_start:
                auto_start.set(1)
            ent_splitname.insert(0, file_splitname)

            ent_title.insert(0, file_title)
            for i, file_outcome in enumerate(file_outcomes):
                outcomes[i].insert(0, file_outcome['title'])

            ent_window.insert(0, file_window)
            
            break


def handle_save():
    outcome_list = validate_form()
    if outcome_list == 1: #not valid form
        return 0

    new_pred_obj = {
        "name": ent_name.get(),
        "auto_predict": {
            "auto_start": bool(auto_start.get()),
            "split_name": ent_splitname.get()
        },
        "data": {
            "broadcaster_id": "",
            "title": ent_title.get(),
            "outcomes": [],
            "prediction_window": int(ent_window.get())
        }        
    }

    for outcome in outcome_list:
        new_pred_obj['data']['outcomes'].append(outcome)

    #check if exists
    for existing_pred in dict['predictions']:
        #modifying existing pred
        if existing_pred['name'] == new_pred_obj['name']:
            #remove existing
            dict['predictions'].pop(dict['predictions'].index(existing_pred))

    #append new or modified pred
    dict['predictions'].append(new_pred_obj)

    with open('predictions/predictions.json', 'w') as file:
        file.write(json.dumps(dict))
    
    lbl_error.config(text="Saved changes", fg="green")

    


def validate_form():
    try:
        lbl_error.config(text="", fg="red")

        if ent_name.get() == "" or len(ent_name.get().split()) != 1:
            lbl_error.config(text="Must set a Name without spaces")
            return 1

        if auto_start.get() and ent_splitname.get() == "":
            lbl_error.config(text="Must set a Split name")
            return 1
        
        if ent_title.get() == "":
            lbl_error.config(text="Must set a Title")
            return 1
        
        outcome_counter = 0
        outcome_list = []
        for outcome in outcomes:
            if outcome.get() != "":
                outcome_list.append({"title": outcome.get()})
                outcome_counter += 1
        
        if not outcome_counter >= 2:
            lbl_error.config(text="Must set at least 2 outcomes")
            return 1
        
        if not 30 <= int(ent_window.get()) <= 1800:
            raise ValueError
        
        return outcome_list
    except ValueError:
            lbl_error.config(text="Window must be a number between 30 and 1800 seconds")
            return 1
    


root = tk.Tk()
root.title("Predictions manager")
root.geometry(newGeometry='700x550')
root.columnconfigure(2)


frm_list = tk.Frame(master=root)
frm_list.grid(column=0, row=0, sticky='w')

sb_scrollx = tk.Scrollbar(master=frm_list, orient='horizontal')
sb_scrollx.pack(side=tk.BOTTOM, fill=tk.X)

sb_scrolly = tk.Scrollbar(master=frm_list, orient='vertical')
sb_scrolly.pack(side=tk.LEFT, fill=tk.Y)

lb_list = tk.Listbox(master=frm_list, xscrollcommand=sb_scrollx.set, yscrollcommand=sb_scrolly.set, cursor='hand2', height=24, selectmode=tk.SINGLE)
lb_list.bind('<<ListboxSelect>>', handle_select_pred)
lb_list.pack(side=tk.LEFT, fill=tk.BOTH)

sb_scrollx.config(command=lb_list.xview)
sb_scrolly.config(command=lb_list.yview)


for i, pred in enumerate(dict['predictions']):
    lb_list.insert(i, pred['name'])


frm_pred = tk.Frame(master=root, borderwidth=2, relief=tk.RAISED)
frm_pred.grid(column=1, row=0, sticky='n')

lbl_name = tk.Label(master=frm_pred, text='Name *')
lbl_name.grid(column=0, row=0, pady=(5,20), sticky='w')
ent_name = tk.Entry(master=frm_pred, width=40 )
ent_name.grid(column=1, row=0, pady=(5,20))


auto_start = tk.IntVar()
lbl_autostart = tk.Label(master=frm_pred, text='Auto start')
lbl_autostart.grid(column=0, row=1, sticky='w')
chk_autostart = tk.Checkbutton(master=frm_pred, variable=auto_start)
chk_autostart.grid(column=1, row=1, sticky='w')

lbl_splitname = tk.Label(master=frm_pred, text='Split name') #only if autostart is ticked
lbl_splitname.grid(column=0, row=2, pady=(5,20), sticky='w')
ent_splitname = tk.Entry(master=frm_pred, width=40 )
ent_splitname.grid(column=1, row=2, pady=(5,20))

lbl_title = tk.Label(master=frm_pred, text='Title *')
lbl_title.grid(column=0, row=3, pady=(0,1), sticky='w')
ent_title = tk.Entry(master=frm_pred, width=40 )
ent_title.grid(column=1, row=3, pady=(0,1))

outcomes = []

for i in range(10):
    if i in (0,1):
        lbl_outcome = tk.Label(master=frm_pred, text=f'Outcome {i+1} *')
    else:
        lbl_outcome = tk.Label(master=frm_pred, text=f'Outcome {i+1}')
    lbl_outcome.grid(column=0, row=4+i, sticky='w', pady=(0,1))
    ent_outcome = tk.Entry(master=frm_pred, width=40 )
    ent_outcome.grid(column=1, row=4+i, pady=(0,1))
    outcomes.append(ent_outcome)

lbl_window = tk.Label(master=frm_pred, text='Window (in seconds) *')
lbl_window.grid(column=0, row=14, pady=(2,1), sticky='w')
ent_window = tk.Entry(master=frm_pred, width=40 )
ent_window.grid(column=1, row=14, pady=(2,1))


frm_buttons = tk.Frame(master=root)
frm_buttons.grid(column=1, row=1)

btn_save = tk.Button(master=frm_buttons, text="Save", padx=20, pady=10, command=handle_save)
btn_save.grid(column=0, row=0, padx=(15,15))

btn_delete = tk.Button(master=frm_buttons, text="Delete", padx=20, pady=10)
btn_delete.grid(column=1, row=0, padx=(15,15))


lbl_error = tk.Label(master=root, text="", foreground="red", font=('Arial', 12))
lbl_error.grid(column=1, row=2, pady=(25,0))






root.mainloop()
