import React, { useState } from 'react';
import { AIAgent } from '../types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Settings, FileText, Edit3 } from 'lucide-react'; // Example icons
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ChatHeaderProps {
  agent: AIAgent;
  chatId: string;
  chatTitle: string; // Assuming you'll manage chat title state
  onTitleChange: (newTitle: string) => void; // Callback to update title
}

export default function ChatHeader({ agent, chatId, chatTitle, onTitleChange }: ChatHeaderProps) {
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [tempTitle, setTempTitle] = useState(chatTitle);

  const handleTitleEdit = () => {
    setIsEditingTitle(true);
    setTempTitle(chatTitle); // Initialize with current title
  };

  const handleTitleSave = () => {
    onTitleChange(tempTitle);
    setIsEditingTitle(false);
  };

  const handleTitleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleTitleSave();
    } else if (e.key === 'Escape') {
      setIsEditingTitle(false);
      setTempTitle(chatTitle); // Revert
    }
  };

  // Placeholder functions for new actions
  const handleSystemPromptSettings = () => alert('System Prompt Settings (Not Implemented)');
  const handleViewContext = () => alert('View Context/Memory (Not Implemented)');

  return (
    <div className="bg-white dark:bg-gray-800 p-3 sm:p-4 border-b border-gray-200 dark:border-gray-700 shadow-sm flex items-center justify-between space-x-2">
      <div className="flex items-center space-x-2 overflow-hidden">
        {isEditingTitle ? (
          <Input
            type="text"
            value={tempTitle}
            onChange={(e) => setTempTitle(e.target.value)}
            onBlur={handleTitleSave} // Save on blur
            onKeyDown={handleTitleKeyDown}
            className="text-lg sm:text-xl font-semibold h-9 flex-grow min-w-0" // flex-grow and min-w-0 for responsiveness
            autoFocus
          />
        ) : (
          <h1
            className="text-lg sm:text-xl font-semibold text-gray-800 dark:text-gray-200 truncate cursor-pointer"
            onClick={handleTitleEdit}
            title="Click to edit title"
          >
            {chatTitle || `Chat with ${agent.name}`} {/* Fallback title */}
          </h1>
        )}
        {!isEditingTitle && (
          <Button variant="ghost" size="icon" onClick={handleTitleEdit} className="flex-shrink-0">
            <Edit3 className="h-4 w-4" />
            <span className="sr-only">Edit Title</span>
          </Button>
        )}
      </div>

      <div className="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 sm:mr-1" />
              <span className="hidden sm:inline">Options</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Chat Options</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleSystemPromptSettings}>
              <Settings className="mr-2 h-4 w-4" />
              <span>System Prompt</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleViewContext}>
              <FileText className="mr-2 h-4 w-4" />
              <span>View Context</span>
            </DropdownMenuItem>
            {/* Add more options here */}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}