# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

        
class CommandContainer(TwiceCommand, Command):
    def __init__(self, description, state, commands):
        Command.__init__(self, description)
        TwiceCommand.__init__(self, state)
        self._commands = commands
        self._reverse = False 
    def _execute_1(self):
        if self._reverse:
            self._commands.reverse()
        for i in self._commands:
            i.execute()
        self._reverse = True
    def _execute_2(self):
        #XXX: Later should be fix because it's only work in state = TRUE!
        self._commands.reverse()
        for i in self._commands:
            i.execute()
    
        
        
    
    
class CommandManager(gobject.GObject):
    __gsignals__ = {
        'changed':  (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                     (gobject.TYPE_STRING,))
        }
    def __init__(self):
        gobject.GObject.__init__(self)
        self._progress = True 
        self._stack = Stack()
    
    # Public API
    def can_undo(self):
        return self._stack.can_undo()
    def can_redo(self):
        return self._stack.can_redo()
    def peek_undo(self):
        '''
        @return: description undo
        @rtype: str
        '''
        return self._stack.peek_undo()
    def peek_redo(self):
        '''
        @return: description redo
        @rtype: str
        '''
        return self._stack.peek_redo()
    def do_undo(self):
        cmd = self._stack.pop_undo()
        cmd.execute()
        self.emit('changed',None )
        #from umit.interfaceeditor.BugDiff import BugDiff
        #BugDiff.plist(self._stack._commands)
        #print self._stack._current_command
    
    def do_redo(self):
        cmd = self._stack.pop_redo()
        cmd.execute()
        self.emit('changed',None )
        #from umit.interfaceeditor import BugDiff
        #BugDiff.plist(self._stack._commands)
        #print self._stack._current_command

    def add_command(self, command):
        self._stack.push(command)
        command.execute()
        self.emit('changed',None )

    
command_manager = CommandManager()    