import React from "react"
import { Button, useToast } from "@chakra-ui/react"
import { TasksService } from "@/client/sdk.gen"

export default function DeleteTask({ id, onDeleted }: { id: number, onDeleted?: () => void }) {
  const toast = useToast()

  const handleDelete = async () => {
    await TasksService.deleteTask({ id })
    toast({ title: "Task deleted", status: "success" })
    onDeleted?.()
  }

  return (
    <Button size="sm" colorScheme="red" onClick={handleDelete}>
      Delete
    </Button>
  )
}
