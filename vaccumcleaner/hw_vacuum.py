def start():
    print("The vacuum has started running")
    print("""1. Solid 
2. Liquid
3. Back to commands""")
    x = int(input("Choose the option to select the categories: "))
    
    if x == 1:
        solid()
    elif x == 2:
        liquid()
    else:
        return

def solid():
    print("""1. Dust
2. Rocks/Papers
3. Others """)
    
    y = int(input("Choose the type of the solid: "))
    
    if y == 1:
        print("The vacuum is sucking the dust")
        print("The shape of the vacuum has changed to rectangle\n")
    elif y == 2:
        print("The vacuum is sucking the rocks/papers")
        print("The shape of the vacuum has changed to circle\n")
    elif y == 3:
        print("The vacuum is sucking the solid")
        print("The shape of the vacuum has changed to square\n")
    else:
        print("Invalid choice for solid\n")

def liquid():
    print("""1. Water
2. Beverage
3. Others""")
    z = int(input("Choose the type of the liquid: "))
    
    if z == 1:
        print("The vacuum is sucking the water")
        print("The shape of vacuum has changed to funnel\n")
    elif z == 2:
        print("The vacuum is sucking the beverage")
        print("The shape of vacuum has changed to funnel\n")
    elif z == 3:
        print("The vacuum is sucking the liquid")
        print("The shape of vacuum has changed to cone\n")
    else:
        print("Invalid choice for liquid\n")

def left():
    print("The vacuum has turned to the left side\n")

def right():
    print("The vacuum has turned to the right side\n")

def dock():
    print("The vacuum is at rest\n")

def main():
    while True:
        print("""    1. Start
    2. Left
    3. Right
    4. Dock
    5. Stop""")
        
        choice = int(input("Choose the command to be instructed: "))
        if choice == 1:
            start()
        elif choice == 2:
            left()
        elif choice == 3:
            right()
        elif choice == 4:
            dock()
        elif choice == 5:
            print("The vacuum has stopped")
            break
        else:
            print("Invalid choice, please try again.")

main()


