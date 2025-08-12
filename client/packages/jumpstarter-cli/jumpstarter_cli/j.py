"""Short alias 'j' for the jmp command."""

# Just import and re-export the main jmp command
from .jmp import jmp as j

if __name__ == "__main__":
    j()
