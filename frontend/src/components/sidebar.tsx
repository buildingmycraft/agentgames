import * as React from "react"

import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
} from "@/components/ui/sidebar"

export function AppSidebar(
  { 
    header,
    content,
   }: { 
    header: React.ReactElement<typeof SidebarHeader>
    content: React.ReactElement<typeof SidebarContent>
  }) {
  return (
    <Sidebar>
      {header}
      {content}
    </Sidebar>
  )
}
