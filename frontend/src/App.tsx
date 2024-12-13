import { useState } from "react";
import { AppSidebar } from "./components/sidebar";
import { 
  SidebarHeader,
  SidebarContent,
 } from "@/components/ui/sidebar";
import { EnvSwitcher } from "./components/environment-switcher";

import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"

import { Separator } from "@/components/ui/separator"

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"

const data = {
  environments: [
    "MathSolver",
  ],
}

const sidebarHeader = (
  <SidebarHeader>
    <EnvSwitcher
      environments={data.environments}
      defaultEnvironment={data.environments[0]}
    />
  </SidebarHeader>
)

const sidebarContent = (
  <SidebarContent>
  </SidebarContent>
)

function App() {
  const [section, setSection] = useState("Sessions")
  const [page, setPage] = useState("New Session")

  return (
    <SidebarProvider>
      <AppSidebar 
        header={sidebarHeader}
        content={sidebarContent}
      />
      <SidebarInset>
      <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem className="hidden md:block">
                <BreadcrumbLink href="#">
                  {section}
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator className="hidden md:block" />
              <BreadcrumbItem>
                <BreadcrumbPage>{page}</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default App;