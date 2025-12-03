// Duplicate of ItemActionsMenu for Tasks
import React from "react"
import { Menu, MenuButton, MenuList, MenuItem, IconButton } from "@chakra-ui/react"
import { FiMoreVertical } from "react-icons/fi"

export function TaskActionsMenu({ task }: { task: any }) {
  return (
    <Menu>
      <MenuButton as={IconButton} icon={<FiMoreVertical />} variant="ghost" />
      <MenuList>
        <MenuItem>Edit</MenuItem>
        <MenuItem>Delete</MenuItem>
      </MenuList>
    </Menu>
  )
}
