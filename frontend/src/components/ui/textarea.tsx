import * as React from "react"

import { cn } from "@/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "placeholder:text-muted-foreground dark:bg-input/30 flex field-sizing-content min-h-16 w-full rounded-md bg-transparent px-3 py-2 text-base shadow-xs transition-all duration-200 outline-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        "border border-gray-200 dark:border-gray-700",
        "focus-visible:border-blue-500 dark:focus-visible:border-cyan-400 focus-visible:ring-2 focus-visible:ring-blue-500/20 dark:focus-visible:ring-cyan-400/20 focus-visible:shadow-[0_0_0_1px_rgb(59,130,246,0.3)] dark:focus-visible:shadow-[0_0_0_1px_rgb(34,211,238,0.3)]",
        "aria-invalid:border-red-500 dark:aria-invalid:border-red-400 aria-invalid:ring-2 aria-invalid:ring-red-500/20 dark:aria-invalid:ring-red-400/20",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }
