import {
    EmptyState,
    Flex,
  
  Table,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"

// Replace ItemsService with TasksService
import { TasksService } from "@/client"
// Replace ItemActionsMenu with TaskActionsMenu
import { TaskActionsMenu } from "@/components/Common/TaskActionsMenu"
// Replace AddItem with AddTask
import AddTask from "@/components/Tasks/AddTask"
// // Replace PendingItems with PendingTasks
import PendingTasks from "@/components/Pending/PendingTasks"
import {
  PaginationItems as PaginationTasks,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"

const tasksSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

function getTasksQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      TasksService.readTasks({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["tasks", { page }],
  }
}

export const Route = createFileRoute("/_layout/tasks")({
  component: Tasks,
  validateSearch: (search) => tasksSearchSchema.parse(search),
})

function TasksTable() {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getTasksQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) => {
    navigate({
      to: "/tasks",
      search: (prev) => ({ ...prev, page }),
    })
  }

  const tasks = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingTasks />
  }

  if (tasks.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>You don't have any tasks yet</EmptyState.Title>
            <EmptyState.Description>
              Add a new task to get started
            </EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">ID</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Title</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Description</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {tasks?.map((task) => (
            <Table.Row key={task.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {task.id}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {task.title}
              </Table.Cell>
              <Table.Cell
                color={!task.description ? "gray" : "inherit"}
                truncate
                maxW="30%"
              >
                {task.description || "N/A"}
              </Table.Cell>
              <Table.Cell>
                <TaskActionsMenu task={task} />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationTasks />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}



import { Box, Container, Text, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import useAuth from "@/hooks/useAuth"

// export const Route = createFileRoute("/_layout/tasks")({
//   component: Tasks,
// })


function Tasks() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Tasks Management
      </Heading>
      <AddTask />
      <TasksTable />
    </Container>
  )
}
