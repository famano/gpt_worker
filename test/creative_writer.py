import random

# Creative Writer Project
# A simple interactive story generator

def story_intro():
    print("Welcome to the Interactive Story Generator!")
    name = input("Enter a name for your main character: ")
    setting = input("Choose a setting (forest, space station, ancient city): ").lower()
    return name, setting


def generate_story(name, setting):
    if setting == 'forest':
        story = f"Once upon a time, {name} wandered into a mysterious forest filled with ancient trees that whispered secrets."
    elif setting == 'space station':
        story = f"In the year 3000, {name} was aboard a space station orbiting a dying star, tasked with saving humanity's last hope."
    elif setting == 'ancient city':
        story = f"Long ago, {name} roamed the streets of an ancient city, searching for lost treasures hidden in its ruins."
    else:
        story = "An error occurred in generating the story due to an unknown setting."
    return story


def main():
    name, setting = story_intro()
    story = generate_story(name, setting)
    print(story)


if __name__ == "__main__":
    main()
