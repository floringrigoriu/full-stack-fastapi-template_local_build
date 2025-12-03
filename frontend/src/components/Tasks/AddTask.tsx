// Duplicate of AddItem for Tasks
import React from "react"
import { useForm } from "react-hook-form"
import { Button, Input, VStack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { TasksService } from "@/client"

export default function AddTask() {
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset } = useForm()
  const mutation = useMutation({
    mutationFn: (data: any) => TasksService.createTask({ requestBody: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] })
      reset()
    },
  })

  return (
    <form onSubmit={handleSubmit((data) => mutation.mutate(data))}>
      <VStack align="stretch" spacing={4} mb={4}>
        <Input {...register("title", { required: true })} placeholder="Task Title" />
        <Input {...register("description")} placeholder="Task Description" />
        <Button type="submit" colorScheme="blue" isLoading={mutation.isLoading}>
          Add Task
        </Button>
      </VStack>
    </form>
  )
}
