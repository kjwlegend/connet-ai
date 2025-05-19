import React from 'react'
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox' // Assuming you've added checkbox via shadcn
import { ScrollArea } from '@/components/ui/scroll-area'

// Mock data for tasks
interface Task {
  id: string
  text: string
  completed: boolean
}

const mockTasks: Task[] = [
  { id: 'task1', text: 'Research latest AI trends', completed: false },
  { id: 'task2', text: 'Draft blog post outline', completed: true },
  { id: 'task3', text: 'Prepare presentation slides', completed: false },
]

export default function TaskGoalManager() {
  const [tasks, setTasks] = React.useState<Task[]>(mockTasks)
  const [newTask, setNewTask] = React.useState('')

  const handleAddTask = () => {
    if (newTask.trim()) {
      setTasks([
        ...tasks,
        { id: Date.now().toString(), text: newTask, completed: false },
      ])
      setNewTask('')
    }
  }

  const toggleTask = (taskId: string) => {
    setTasks(
      tasks.map((task) =>
        task.id === taskId ? { ...task, completed: !task.completed } : task
      )
    )
  }

  return (
    <div className="w-1/4 min-w-[250px] max-w-[350px] bg-gray-100 dark:bg-gray-850 p-4 border-l border-gray-300 dark:border-gray-700 flex-shrink-0">
      <Card className="h-full flex flex-col">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            Tasks & Goals
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden">
          <ScrollArea className="h-full pr-2">
            {' '}
            {/* Added pr-2 for scrollbar space */}
            {tasks.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No tasks yet. Add one below!
              </p>
            ) : (
              <ul className="space-y-2">
                {tasks.map((task) => (
                  <li
                    key={task.id}
                    className="flex items-center space-x-2 p-2 bg-white dark:bg-gray-700 rounded-md shadow-sm"
                  >
                    <Checkbox
                      id={`task-${task.id}`}
                      checked={task.completed}
                      onCheckedChange={() => toggleTask(task.id)}
                    />
                    <label
                      htmlFor={`task-${task.id}`}
                      className={`flex-1 text-sm cursor-pointer ${
                        task.completed
                          ? 'line-through text-gray-500 dark:text-gray-400'
                          : 'text-gray-800 dark:text-gray-200'
                      }`}
                    >
                      {task.text}
                    </label>
                  </li>
                ))}
              </ul>
            )}
          </ScrollArea>
        </CardContent>
        <CardFooter className="border-t pt-4">
          <div className="flex w-full space-x-2">
            <Input
              type="text"
              placeholder="Add a new task..."
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddTask()}
              className="flex-1"
            />
            <Button onClick={handleAddTask}>Add</Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
