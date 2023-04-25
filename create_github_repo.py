import os
import subprocess
import click
from github import Github

# Retrieve the GitHub access token from the environment variable
GITHUB_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
USERNAME = "oliverproudfoot"

if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_ACCESS_TOKEN environment variable.")

def create_gitignore(extensions):
    """Create or update a .gitignore file with the given file extensions."""
    if not os.path.exists(".gitignore"):
        with open(".gitignore", "w") as f:
            for ext in extensions:
                f.write(f"*{ext}\n")
    else:
        with open(".gitignore", "a") as f:
            for ext in extensions:
                f.write(f"*{ext}\n")

@click.command()
@click.option('--name', prompt='Please enter the name of the repository', help='Name of the GitHub repository.')
@click.option('--private', default=None, help='Set the repository type to private or public. If not provided, it will ask for input.')
@click.option('--upload_cwd', default=None, help='Upload the current working directory to the new repository.')
def create_github_repo(name, private, upload_cwd):
    """Create a new GitHub repository."""

    github = Github(GITHUB_TOKEN)
    user = github.get_user()

    # Ask for the repository type (private or public) if not provided
    if private is None:
        private = click.prompt("Do you want to create a private repository? (yes/no)", type=bool, default=False)

    # Ask if the user wants to upload the current working directory if not provided
    if upload_cwd is None:
        upload_cwd = click.prompt("Do you want to upload the current working directory? (yes/no)", type=bool, default=False)

    try:
        repo = user.create_repo(name, private=private)
        click.echo(click.style(f'Successfully created repository: {repo.html_url}', fg='green'))

        # Use the SSH URL for cloning
        clone_url_ssh = repo.ssh_url

        if upload_cwd:
            # Suggest a .gitignore file with certain file extensions
            extensions = ['.pyc', '.log', '.tmp', '.DS_Store', '.csv', '.tsv', '.env','.ENV']
            create_gitignore(extensions)
            click.echo(click.style(f'Successfully created or updated .gitignore with suggested file extensions.', fg='green'))

            # Initialize the current working directory as a Git repository if needed
            if not os.path.exists(".git"):
                subprocess.run(['git', 'init'])

            # Add the newly created repository as a remote
            subprocess.run(['git', 'remote', 'add', 'origin', clone_url_ssh])

            # Push the current working directory to the newly created repository
            subprocess.run(['git', 'add', '.'])
            subprocess.run(['git', 'commit', '-m', 'Initial commit'])
            subprocess.run(['git', 'push', '-u', 'origin', 'main'])
            click.echo(click.style(f'Successfully pushed the current working directory to the repository.', fg='green'))
        else:
            # Clone the newly created repository to the current working directory using SSH
            subprocess.run(['git', 'clone', clone_url_ssh])
            click.echo(click.style(f'Successfully cloned repository to the current working directory.', fg='green'))

    except Exception as e:
        click.echo(click.style(f'Error creating repository: {str(e)}', fg='red'))

if __name__ == '__main__':
    create_github_repo()
    
