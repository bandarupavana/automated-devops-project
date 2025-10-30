from flask import Flask, request, redirect, url_for
import os

app = Flask(__name__)

# --- In-memory storage for To-Do items ---
# NOTE: Data is lost when the server restarts.
todo_list = [
    {"id": 1, "text": "Set up GKE Cluster using Terraform", "done": True},
    {"id": 2, "text": "Configure Cloud Build Trigger", "done": False},
    {"id": 3, "text": "Deploy To-Do App via CI/CD", "done": False}
]
next_id = 4 # Tracks the next unique ID

def render_todo_html(todos):
    """Generates the main HTML structure with Tailwind CSS for aesthetics."""
    
    # Load Tailwind CSS CDN for styling and use the Inter font
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beautiful To-Do List</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
        }
    </style>
</head>
<body class="p-4 sm:p-8 min-h-screen flex items-start justify-center">
    <div class="w-full max-w-lg bg-white shadow-2xl rounded-xl p-6 sm:p-8 mt-10">
        <h1 class="text-3xl font-bold text-gray-800 border-b-2 border-indigo-500 pb-2 mb-6 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-indigo-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            DevOps To-Do List
        </h1>

        <!-- Add New Item Form -->
        <form method="POST" action="/" class="mb-8 flex space-x-2">
            <input type="text" name="text" required placeholder="New task..."
                   class="flex-grow p-3 border-2 border-indigo-300 rounded-lg focus:outline-none focus:border-indigo-500 transition duration-200 shadow-sm"
                   maxlength="100">
            <button type="submit" name="action" value="add"
                    class="px-4 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition duration-200 shadow-md flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                Add
            </button>
        </form>

        <!-- To-Do List -->
        <div id="todo-list">
    """
    
    if not todos:
        html_content += """
        <p class="text-center text-gray-500 py-6 border-2 border-dashed border-gray-300 rounded-lg">
            All tasks complete! Time for a coffee.
        </p>
        """
    else:
        for todo in todos:
            # Conditional styling based on 'done' status
            status_class = "text-gray-500 bg-gray-100 border-gray-100" if todo['done'] else "text-gray-800 bg-white hover:bg-indigo-50 border-gray-200"
            checkbox_checked = "checked" if todo['done'] else ""
            
            html_content += f"""
            <div class="flex items-center justify-between p-4 mb-3 rounded-lg shadow-sm border {status_class}">
                <form method="POST" action="/" class="flex items-center flex-grow space-x-3">
                    <input type="hidden" name="id" value="{todo['id']}">
                    <input type="checkbox" name="action" value="toggle" onchange="this.form.submit()" {checkbox_checked}
                           class="h-5 w-5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500 cursor-pointer">
                    <span class="text-base font-medium {"line-through" if todo['done'] else ""}">{todo['text']}</span>
                </form>
                
                <form method="POST" action="/" class="ml-4">
                    <input type="hidden" name="id" value="{todo['id']}">
                    <button type="submit" name="action" value="delete"
                            class="text-red-500 hover:text-red-700 p-1 rounded-full hover:bg-red-100 transition duration-150"
                            title="Delete Task">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 10-2 0v6a1 1 0 102 0V8z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </form>
            </div>
            """

    html_content += """
        </div>
        <p class="text-xs text-center text-gray-400 mt-6">
            Data is stored in-memory and will be lost if the server is restarted.
        </p>
    </div>
</body>
</html>
    """
    return html_content


@app.route('/', methods=['GET', 'POST'])
def todo_manager():
    global next_id
    global todo_list

    if request.method == 'POST':
        action = request.form.get('action')
        # Item ID is passed in both delete and toggle forms
        item_id = request.form.get('id', type=int)
        
        if action == 'add':
            text = request.form.get('text', '').strip()
            if text:
                todo_list.append({"id": next_id, "text": text, "done": False})
                next_id += 1
        
        elif action == 'toggle' and item_id is not None:
            for item in todo_list:
                if item['id'] == item_id:
                    item['done'] = not item['done']
                    break
        
        elif action == 'delete' and item_id is not None:
            todo_list = [item for item in todo_list if item['id'] != item_id]
            
        # Always redirect after POST to prevent duplicate submissions
        return redirect(url_for('todo_manager'))

    # Sort the list: incomplete tasks first (False < True)
    sorted_todos = sorted(todo_list, key=lambda x: x['done'])
    
    return render_todo_html(sorted_todos)

if __name__ == '__main__':
    # Listen on 0.0.0.0 for containerization (GKE standard practice)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
