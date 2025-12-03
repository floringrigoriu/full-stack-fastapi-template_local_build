// Duplicate of PendingItems for Tasks
import React from "react"
import { Spinner, Center } from "@chakra-ui/react"

export default function PendingTasks() {
  return (
    <Center py={10}>
      <Spinner size="xl" />
    </Center>
  )
}
