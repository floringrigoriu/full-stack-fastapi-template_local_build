// Duplicate of ItemActionsMenu for Tasks
import React from "react"
import { Menu, IconButton, MenuTrigger ,MenuContent,MenuRoot} from "@chakra-ui/react"
import { FiMoreVertical } from "react-icons/fi"
import { BsThreeDotsVertical } from "react-icons/bs"
import EditTask from "../Tasks/EditTask"
import DeleteTask from "../Tasks/DeleteTask"

export function TaskActionsMenu({ task, onUpdated, onDeleted }: { task: any, onUpdated?: () => void, onDeleted?: () => void }) {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit" >
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <EditTask task={task} onUpdated={onUpdated} />
        {/* <DeleteTask id={task.id} onDeleted={onDeleted} /> */}
      </MenuContent>
    </MenuRoot>
  )
}
