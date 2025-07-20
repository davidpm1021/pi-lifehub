// Pi Life Hub - Touch-optimized JavaScript

class LifeHub {
    constructor() {
        this.currentUser = null;
        this.users = [];
        this.todos = [];
        this.init();
    }

    async init() {
        await this.loadUsers();
        this.updateTime();
        this.setupEventListeners();
        
        // Update time every second
        setInterval(() => this.updateTime(), 1000);
        
        // Refresh data every 30 seconds
        setInterval(() => this.refreshData(), 30000);
    }

    async updateTime() {
        try {
            const response = await fetch('/api/time');
            const data = await response.json();
            
            document.getElementById('current-time').textContent = data.time;
            document.getElementById('current-date').textContent = data.date;
        } catch (error) {
            console.error('Failed to update time:', error);
            // Fallback to client-side time in Eastern Time
            const now = new Date();
            document.getElementById('current-time').textContent = 
                now.toLocaleTimeString('en-US', {
                    hour: 'numeric', 
                    minute: '2-digit', 
                    hour12: true,
                    timeZone: 'America/New_York'
                });
            document.getElementById('current-date').textContent = 
                now.toLocaleDateString('en-US', {
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric',
                    timeZone: 'America/New_York'
                });
        }
    }

    async loadUsers() {
        try {
            const response = await fetch('/api/users');
            this.users = await response.json();
            this.populateUserSelect();
        } catch (error) {
            console.error('Failed to load users:', error);
            // Create default family members if none exist
            await this.createDefaultUsers();
        }
    }

    async createDefaultUsers() {
        const defaultUsers = ['Dad', 'Mom', 'Kid 1', 'Kid 2'];
        
        for (const name of defaultUsers) {
            try {
                await fetch('/api/users', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name})
                });
            } catch (error) {
                console.error(`Failed to create user ${name}:`, error);
            }
        }
        
        await this.loadUsers();
    }

    populateUserSelect() {
        const select = document.getElementById('user-select');
        select.innerHTML = '<option value="">Select Family Member</option>';
        
        this.users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.name;
            select.appendChild(option);
        });
    }

    async selectUser(userId) {
        this.currentUser = userId ? this.users.find(u => u.id == userId) : null;
        
        if (this.currentUser) {
            await this.loadTodos();
            document.querySelector('.todo-input').style.display = 'flex';
        } else {
            this.todos = [];
            this.renderTodos();
            document.querySelector('.todo-input').style.display = 'none';
        }
    }

    async loadTodos() {
        if (!this.currentUser) return;
        
        try {
            const response = await fetch(`/api/todos/${this.currentUser.id}`);
            this.todos = await response.json();
            this.renderTodos();
        } catch (error) {
            console.error('Failed to load todos:', error);
        }
    }

    renderTodos() {
        const todoList = document.getElementById('todo-list');
        
        if (!this.currentUser) {
            todoList.innerHTML = '<p class="empty-state">Select a family member to view tasks</p>';
            return;
        }

        if (this.todos.length === 0) {
            todoList.innerHTML = '<p class="empty-state">No tasks yet. Add one below!</p>';
            return;
        }

        todoList.innerHTML = this.todos.map(todo => `
            <div class="todo-item">
                <input type="checkbox" class="todo-checkbox" 
                       ${todo.completed ? 'checked' : ''} 
                       onchange="lifeHub.toggleTodo(${todo.id}, this.checked)">
                <span class="todo-text ${todo.completed ? 'completed' : ''}">${todo.task}</span>
            </div>
        `).join('');
    }

    async addTodo() {
        const input = document.getElementById('new-todo');
        const task = input.value.trim();
        
        if (!task || !this.currentUser) return;

        try {
            const response = await fetch(`/api/todos/${this.currentUser.id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task})
            });

            if (response.ok) {
                input.value = '';
                await this.loadTodos();
                this.showFeedback('Task added!');
            }
        } catch (error) {
            console.error('Failed to add todo:', error);
            this.showFeedback('Failed to add task', 'error');
        }
    }

    async toggleTodo(todoId, completed) {
        try {
            const response = await fetch(`/api/todos/${todoId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({completed})
            });

            if (response.ok) {
                await this.loadTodos();
                this.showFeedback(completed ? 'Task completed!' : 'Task unchecked');
            }
        } catch (error) {
            console.error('Failed to toggle todo:', error);
            this.showFeedback('Failed to update task', 'error');
        }
    }

    setupEventListeners() {
        // User selection
        document.getElementById('user-select').addEventListener('change', (e) => {
            this.selectUser(e.target.value);
        });

        // Add todo on Enter key
        document.getElementById('new-todo').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addTodo();
            }
        });

        // Add todo button
        document.getElementById('add-todo').addEventListener('click', () => {
            this.addTodo();
        });

        // Touch feedback for buttons
        document.querySelectorAll('button, .action-btn').forEach(btn => {
            btn.addEventListener('touchstart', () => {
                btn.style.transform = 'scale(0.95)';
            });
            btn.addEventListener('touchend', () => {
                btn.style.transform = '';
            });
        });
    }

    async refreshData() {
        if (this.currentUser) {
            await this.loadTodos();
        }
        await this.loadUsers();
    }

    showFeedback(message, type = 'success') {
        // Create temporary feedback element
        const feedback = document.createElement('div');
        feedback.textContent = message;
        feedback.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: ${type === 'error' ? '#f44336' : '#4CAF50'};
            color: white;
            border-radius: 8px;
            z-index: 1001;
            opacity: 0;
            transition: opacity 0.3s;
        `;
        
        document.body.appendChild(feedback);
        
        // Animate in
        setTimeout(() => feedback.style.opacity = '1', 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            feedback.style.opacity = '0';
            setTimeout(() => feedback.remove(), 300);
        }, 3000);
    }
}

// Quick action functions
function startTimer() {
    showModal(`
        <h2>Quick Timer</h2>
        <div style="text-align: center; padding: 20px;">
            <p>Timer feature coming soon!</p>
            <p style="margin-top: 20px; opacity: 0.7;">Will support preset times for common tasks</p>
        </div>
    `);
}

function showNFC() {
    showModal(`
        <h2>NFC Setup</h2>
        <div style="padding: 20px;">
            <p>NFC tag reader coming soon!</p>
            <p style="margin-top: 15px; opacity: 0.7;">Each family member will have their own NFC tag for quick profile switching</p>
        </div>
    `);
}

function showPhotos() {
    showModal(`
        <h2>Family Photos</h2>
        <div style="text-align: center; padding: 20px;">
            <p>Photo slideshow coming soon!</p>
            <p style="margin-top: 15px; opacity: 0.7;">Will display family photos from local storage</p>
        </div>
    `);
}

function showSettings() {
    showModal(`
        <h2>Settings</h2>
        <div style="padding: 20px;">
            <p>Settings panel coming soon!</p>
            <ul style="margin-top: 15px; opacity: 0.7; list-style: none;">
                <li>• Wi-Fi configuration</li>
                <li>• Display brightness</li>
                <li>• Family member management</li>
                <li>• System updates</li>
            </ul>
        </div>
    `);
}

function showModal(content) {
    document.getElementById('modal-body').innerHTML = content;
    document.getElementById('modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

// Initialize the app
const lifeHub = new LifeHub();

// Global error handling
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    lifeHub.showFeedback('Something went wrong', 'error');
});

// Handle offline/online status
window.addEventListener('offline', () => {
    lifeHub.showFeedback('Working offline', 'error');
});

window.addEventListener('online', () => {
    lifeHub.showFeedback('Back online');
    lifeHub.refreshData();
});