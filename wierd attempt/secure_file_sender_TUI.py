import os
import select
import sys
import asyncio
import time
import aioconsole

class TerminalUserInterface:
    def __init__(self, Leaf_Factory, Communication_Factory, state):
        self.leaffactory = Leaf_Factory
        self.communicationfactory = Communication_Factory
        self.state = state
    
    async def singleInput(self, prompt):
        print("Single input")
        try:
            while not self.state.interruptSignal.is_set():
                try:
                    result = await asyncio.wait_for(aioconsole.ainput(prompt), timeout=0.1)
                    return result
                except asyncio.TimeoutError:
                    pass
                except asyncio.CancelledError:
                    print("\nInput operation cancelled!")
                    return None
            print("\nInput interrupted.")
            return None
        except asyncio.CancelledError:
            print("\nInput operation cancelled!")
            return None
    
    async def multiInput(self):
        pass
    
    async def promptUltrapeer(self):
        print("Prompting ultrapeer")
        # Check state
        
        # Take input
        user_input_task = asyncio.create_task(self.singleInput("> "))
        user_input = await user_input_task
        
        # Handle input
        match user_input:
            case "help":
                print("\nHelp message")
            case _:
                print("::",user_input)
                self.leaffactory.protocol.dataSend(user_input)
        pass
    
    def promptCommmunication(self):
        pass
    
    async def interfaceLoop(self):
        while self.state.running:
            if self.state.ultrapeerConnection:
                if self.state.ultrapeerAwaitingInput:
                    await asyncio.sleep(0.1)
                    await self.promptUltrapeer()
            await asyncio.sleep(0.01)