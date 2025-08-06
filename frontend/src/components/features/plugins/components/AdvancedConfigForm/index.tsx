"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Checkbox } from "@/components/ui/checkbox"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Settings, 
  Key, 
  Globe, 
  Database, 
  ChevronDown, 
  ChevronRight,
  HelpCircle,
  AlertCircle,
  CheckCircle,
  Save,
  TestTube
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useTheme } from "next-themes"
import type { Plugin, ConfigField, SelectConfigField, NumberConfigField } from "@/types/plugin"

interface AdvancedConfigFormProps {
  plugin: Plugin
  onSave: (config: Record<string, any>) => Promise<void>
  onTest?: (config: Record<string, any>) => Promise<void>
  isSaving?: boolean
  isTesting?: boolean
  testResult?: { success: boolean; message: string } | null
}

export function AdvancedConfigForm({ 
  plugin, 
  onSave, 
  onTest,
  isSaving = false,
  isTesting = false,
  testResult
}: AdvancedConfigFormProps) {
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({})
  const [errors, setErrors] = useState<Record<string, string>>({})
  const { theme } = useTheme()

  // 初始化表单数据
  useEffect(() => {
    const initialData: Record<string, any> = {}
    
    plugin.configTemplate.sections.forEach(section => {
      section.fields.forEach(field => {
        if (field.defaultValue !== undefined) {
          initialData[field.key] = field.defaultValue
        } else if (plugin.currentConfig && plugin.currentConfig[field.key] !== undefined) {
          initialData[field.key] = plugin.currentConfig[field.key]
        }
      })
    })
    
    setFormData(initialData)

    // 设置默认展开状态
    const defaultExpanded: Record<string, boolean> = {}
    plugin.configTemplate.sections.forEach(section => {
      defaultExpanded[section.id] = !section.defaultCollapsed
    })
    setExpandedSections(defaultExpanded)
  }, [plugin])

  const handleFieldChange = (fieldKey: string, value: any) => {
    setFormData(prev => ({ ...prev, [fieldKey]: value }))
    
    // 清除该字段的错误
    if (errors[fieldKey]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[fieldKey]
        return newErrors
      })
    }
  }

  const validateField = (field: ConfigField, value: any): string | null => {
    if (field.required && (value === undefined || value === null || value === "")) {
      return `${field.label} 是必填项`
    }

    if (field.validation) {
      const { validation } = field
      
      if (validation.minLength && typeof value === 'string' && value.length < validation.minLength) {
        return `${field.label} 最少需要 ${validation.minLength} 个字符`
      }
      
      if (validation.maxLength && typeof value === 'string' && value.length > validation.maxLength) {
        return `${field.label} 最多允许 ${validation.maxLength} 个字符`
      }
      
      if (validation.min !== undefined && typeof value === 'number' && value < validation.min) {
        return `${field.label} 不能小于 ${validation.min}`
      }
      
      if (validation.max !== undefined && typeof value === 'number' && value > validation.max) {
        return `${field.label} 不能大于 ${validation.max}`
      }
      
      if (validation.pattern && typeof value === 'string') {
        const regex = new RegExp(validation.pattern)
        if (!regex.test(value)) {
          return `${field.label} 格式不正确`
        }
      }
      
      if (validation.custom) {
        const result = validation.custom(value)
        if (typeof result === 'string') {
          return result
        } else if (!result) {
          return `${field.label} 验证失败`
        }
      }
    }
    
    return null
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    plugin.configTemplate.sections.forEach(section => {
      section.fields.forEach(field => {
        const error = validateField(field, formData[field.key])
        if (error) {
          newErrors[field.key] = error
        }
      })
    })
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSave = async () => {
    if (validateForm()) {
      await onSave(formData)
    }
  }

  const handleTest = async () => {
    if (validateForm() && onTest) {
      await onTest(formData)
    }
  }

  const renderField = (field: ConfigField) => {
    const value = formData[field.key]
    const error = errors[field.key]
    
    const fieldProps = {
      id: field.key,
      disabled: field.disabled || field.readonly,
      className: cn(error && "border-red-500")
    }

    let fieldComponent: React.ReactNode

    switch (field.type) {
      case 'text':
      case 'email':
      case 'url':
        fieldComponent = (
          <Input
            {...fieldProps}
            type={field.type}
            value={value || ""}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            placeholder={field.placeholder}
          />
        )
        break

      case 'password':
        fieldComponent = (
          <Input
            {...fieldProps}
            type="password"
            value={value || ""}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            placeholder={field.placeholder}
          />
        )
        break

      case 'number':
        const numberField = field as NumberConfigField
        fieldComponent = (
          <Input
            {...fieldProps}
            type="number"
            value={value || ""}
            onChange={(e) => handleFieldChange(field.key, Number(e.target.value))}
            min={numberField.min}
            max={numberField.max}
            step={numberField.step}
            placeholder={field.placeholder}
          />
        )
        break

      case 'slider':
        const sliderField = field as NumberConfigField
        fieldComponent = (
          <div className="space-y-2">
            <Slider
              {...fieldProps}
              value={[value || sliderField.min || 0]}
              onValueChange={(vals) => handleFieldChange(field.key, vals[0])}
              min={sliderField.min || 0}
              max={sliderField.max || 100}
              step={sliderField.step || 1}
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>{sliderField.min || 0}</span>
              <span className="font-medium">{value || sliderField.min || 0}</span>
              <span>{sliderField.max || 100}</span>
            </div>
          </div>
        )
        break

      case 'textarea':
        fieldComponent = (
          <Textarea
            {...fieldProps}
            value={value || ""}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            placeholder={field.placeholder}
            rows={3}
          />
        )
        break

      case 'select':
        const selectField = field as SelectConfigField
        fieldComponent = (
          <Select value={value || ""} onValueChange={(val) => handleFieldChange(field.key, val)}>
            <SelectTrigger {...fieldProps}>
              <SelectValue placeholder={field.placeholder || `选择${field.label}`} />
            </SelectTrigger>
            <SelectContent>
              {selectField.options.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  <div className="flex items-center space-x-2">
                    {option.icon && <span>{option.icon}</span>}
                    <div>
                      <div>{option.label}</div>
                      {option.description && (
                        <div className="text-xs text-gray-500">{option.description}</div>
                      )}
                    </div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )
        break

      case 'multiselect':
        const multiselectField = field as SelectConfigField
        const selectedValues = Array.isArray(value) ? value : []
        fieldComponent = (
          <div className="space-y-2">
            <div className="flex flex-wrap gap-2 min-h-[2rem] p-2 border rounded-md">
              {selectedValues.map((val: any) => {
                const option = multiselectField.options.find(opt => opt.value === val)
                return option ? (
                  <Badge key={val} variant="secondary" className="text-xs">
                    {option.label}
                    <button 
                      onClick={() => {
                        const newValues = selectedValues.filter((v: any) => v !== val)
                        handleFieldChange(field.key, newValues)
                      }}
                      className="ml-1 hover:text-red-500"
                    >
                      ×
                    </button>
                  </Badge>
                ) : null
              })}
            </div>
            <Select onValueChange={(val) => {
              if (!selectedValues.includes(val)) {
                handleFieldChange(field.key, [...selectedValues, val])
              }
            }}>
              <SelectTrigger>
                <SelectValue placeholder="添加选项..." />
              </SelectTrigger>
              <SelectContent>
                {multiselectField.options
                  .filter(option => !selectedValues.includes(option.value))
                  .map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>
        )
        break

      case 'checkbox':
      case 'toggle':
        fieldComponent = (
          <div className="flex items-center space-x-2">
            {field.type === 'checkbox' ? (
              <Checkbox
                checked={value || false}
                onCheckedChange={(checked) => handleFieldChange(field.key, checked)}
                disabled={field.disabled}
              />
            ) : (
              <Switch
                checked={value || false}
                onCheckedChange={(checked) => handleFieldChange(field.key, checked)}
                disabled={field.disabled}
              />
            )}
            <Label htmlFor={field.key} className="text-sm">
              启用 {field.label}
            </Label>
          </div>
        )
        break

      default:
        fieldComponent = (
          <Input
            {...fieldProps}
            value={value || ""}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            placeholder={field.placeholder}
          />
        )
    }

    return (
      <div key={field.key} className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor={field.key} className="flex items-center space-x-2 text-sm font-medium">
            <span>{field.label}</span>
            {field.required && <span className="text-red-500">*</span>}
            {getFieldIcon(field)}
            {field.tooltip && (
              <HelpCircle className="h-4 w-4 text-gray-400" title={field.tooltip} />
            )}
          </Label>
        </div>
        
        {field.description && (
          <p className={cn(
            "text-xs",
            theme === 'dark' ? "text-gray-400" : "text-gray-600"
          )}>
            {field.description}
          </p>
        )}
        
        {fieldComponent}
        
        {error && (
          <p className="text-xs text-red-500 flex items-center space-x-1">
            <AlertCircle className="h-3 w-3" />
            <span>{error}</span>
          </p>
        )}
      </div>
    )
  }

  const getFieldIcon = (field: ConfigField) => {
    if (field.type === "password") return <Key className="h-3 w-3 text-gray-400" />
    if (field.type === "url") return <Globe className="h-3 w-3 text-gray-400" />
    if (field.key.includes("db")) return <Database className="h-3 w-3 text-gray-400" />
    return null
  }

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }))
  }

  return (
    <div className="space-y-6">
      {testResult && (
        <Alert className={testResult.success ? "border-green-500" : "border-red-500"}>
          {testResult.success ? (
            <CheckCircle className="h-4 w-4" />
          ) : (
            <AlertCircle className="h-4 w-4" />
          )}
          <AlertDescription>{testResult.message}</AlertDescription>
        </Alert>
      )}

      {plugin.configTemplate.sections.map((section) => (
        <div key={section.id} className="space-y-4">
          {section.collapsible ? (
            <Collapsible open={expandedSections[section.id]}>
              <CollapsibleTrigger
                onClick={() => toggleSection(section.id)}
                className="flex items-center justify-between w-full p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <div>
                  <h3 className="font-medium text-lg">{section.title}</h3>
                  {section.description && (
                    <p className={cn(
                      "text-sm mt-1",
                      theme === 'dark' ? "text-gray-400" : "text-gray-600"
                    )}>
                      {section.description}
                    </p>
                  )}
                </div>
                {expandedSections[section.id] ? (
                  <ChevronDown className="h-5 w-5" />
                ) : (
                  <ChevronRight className="h-5 w-5" />
                )}
              </CollapsibleTrigger>
              
              <CollapsibleContent className="space-y-4 pt-2">
                {section.fields.map(renderField)}
              </CollapsibleContent>
            </Collapsible>
          ) : (
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-lg">{section.title}</h3>
                {section.description && (
                  <p className={cn(
                    "text-sm mt-1",
                    theme === 'dark' ? "text-gray-400" : "text-gray-600"
                  )}>
                    {section.description}
                  </p>
                )}
              </div>
              <div className="space-y-4">
                {section.fields.map(renderField)}
              </div>
            </div>
          )}
        </div>
      ))}

      {/* Action Buttons */}
      <div className="flex space-x-3 pt-6 border-t">
        <Button 
          onClick={handleSave} 
          disabled={isSaving}
          className="flex-1"
        >
          <Save className="h-4 w-4 mr-2" />
          {isSaving ? "保存中..." : "保存配置"}
        </Button>
        
        {onTest && (
          <Button 
            variant="outline" 
            onClick={handleTest}
            disabled={isTesting}
            className="flex-1"
          >
            <TestTube className="h-4 w-4 mr-2" />
            {isTesting ? "测试中..." : "测试连接"}
          </Button>
        )}
      </div>
    </div>
  )
}

export default AdvancedConfigForm