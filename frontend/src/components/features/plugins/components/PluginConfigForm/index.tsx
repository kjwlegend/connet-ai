"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Settings, Key, Globe, Database } from "lucide-react"
import { useState } from "react"
import type { Plugin } from "../PluginCard"

interface PluginConfigFormProps {
  plugin: Plugin
  onSave: (config: Record<string, any>) => void
  onTest?: () => void
}

export function PluginConfigForm({ plugin, onSave, onTest }: PluginConfigFormProps) {
  const [configValues, setConfigValues] = useState<Record<string, any>>({})

  const handleConfigChange = (key: string, value: any) => {
    setConfigValues((prev) => ({ ...prev, [key]: value }))
  }

  const handleSaveConfig = () => {
    onSave(configValues)
  }

  const renderConfigField = (field: any) => {
    const value = configValues[field.key] || ""

    switch (field.type) {
      case "password":
        return (
          <Input
            type="password"
            value={value}
            onChange={(e) => handleConfigChange(field.key, e.target.value)}
            placeholder={`请输入${field.label}`}
          />
        )
      case "url":
        return (
          <Input
            type="url"
            value={value}
            onChange={(e) => handleConfigChange(field.key, e.target.value)}
            placeholder={`请输入${field.label}`}
          />
        )
      case "number":
        return (
          <Input
            type="number"
            value={value}
            onChange={(e) => handleConfigChange(field.key, e.target.value)}
            min={field.min}
            max={field.max}
            step={field.step}
            placeholder={`请输入${field.label}`}
          />
        )
      case "select":
        return (
          <Select value={value} onValueChange={(val) => handleConfigChange(field.key, val)}>
            <SelectTrigger>
              <SelectValue placeholder={`选择${field.label}`} />
            </SelectTrigger>
            <SelectContent>
              {field.options?.map((option: string) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )
      case "checkbox":
        return (
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={value}
              onChange={(e) => handleConfigChange(field.key, e.target.checked)}
              className="rounded"
            />
            <span className="text-sm">启用{field.label}</span>
          </div>
        )
      case "textarea":
        return (
          <Textarea
            value={value}
            onChange={(e) => handleConfigChange(field.key, e.target.value)}
            placeholder={`请输入${field.label}`}
            rows={3}
          />
        )
      default:
        return (
          <Input
            value={value}
            onChange={(e) => handleConfigChange(field.key, e.target.value)}
            placeholder={`请输入${field.label}`}
          />
        )
    }
  }

  const getFieldIcon = (field: any) => {
    if (field.type === "password") return <Key className="h-3 w-3 text-gray-400" />
    if (field.type === "url") return <Globe className="h-3 w-3 text-gray-400" />
    if (field.key.includes("db")) return <Database className="h-3 w-3 text-gray-400" />
    return null
  }

  return (
    <div className="space-y-4">
      {plugin.configFields.map((field) => (
        <div key={field.key} className="space-y-2">
          <Label htmlFor={field.key} className="flex items-center space-x-2">
            <span>{field.label}</span>
            {field.required && <span className="text-red-500">*</span>}
            {getFieldIcon(field)}
          </Label>
          {renderConfigField(field)}
        </div>
      ))}

      <div className="flex space-x-3 pt-4 border-t">
        <Button onClick={handleSaveConfig} className="flex-1">
          <Settings className="h-4 w-4 mr-2" />
          保存配置
        </Button>
        {onTest && (
          <Button variant="outline" className="flex-1 bg-transparent" onClick={onTest}>
            测试连接
          </Button>
        )}
      </div>
    </div>
  )
}

export default PluginConfigForm