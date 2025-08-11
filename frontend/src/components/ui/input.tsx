import * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 flex h-9 w-full min-w-0 rounded-md bg-transparent px-3 py-1 text-base shadow-xs transition-all duration-200 outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        "border border-gray-200 dark:border-gray-700",
        "focus-visible:border-blue-500 dark:focus-visible:border-cyan-400 focus-visible:ring-2 focus-visible:ring-blue-500/20 dark:focus-visible:ring-cyan-400/20 focus-visible:shadow-[0_0_0_1px_rgb(59,130,246,0.3)] dark:focus-visible:shadow-[0_0_0_1px_rgb(34,211,238,0.3)]",
        "aria-invalid:border-red-500 dark:aria-invalid:border-red-400 aria-invalid:ring-2 aria-invalid:ring-red-500/20 dark:aria-invalid:ring-red-400/20",
        className
      )}
      {...props}
    />
  )
}

export { Input }
