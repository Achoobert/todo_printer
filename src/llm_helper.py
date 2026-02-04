import google.genai

# call gemini
def expand_task(task_from_user):
   API_TOKEN = os.getenv("GEMINI_API_KEY")
   google.genai.configure(API_TOKEN)
   model = google.genai.GenerativeModel('gemini-2.5-flash-lite')

   #! wip Prompt
   initial_prompt = """Return in this Format:
```
Title of Task
1m Micro sub-task
5-10 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-15 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-15 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-10 minute sub-task
5-15 minute sub-task
Total Time
```
   Expecting return similar to this
```
Yardwork
1m  walk outside
5m  get out mower
10m mow front lawn
10m mow side lawn
10m rake 
15m review watering system
5m  get out weedwacker
5m  trim around sidewalk
15m clean up tools
76m Total
```
Notes: first item should take no more than 5 minutes, in order to prime the task"""""
   response = model.generate_content(initial_prompt + task_from_user)
   return response.text.strip().replace("```", "")


# expand_task("Add sound effects to my Godot Card game")
