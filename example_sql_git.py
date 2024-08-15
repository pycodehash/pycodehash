import subprocess
from typing import Literal

import sqlfluff
from pycodehash.sql.sql_hasher import SQLHasher


def git_show_file(commit_id: str, file_name: str) -> str:
    """Get the contents of a file at a specific commit via `git show`

    Args:
        commit_id: the commit SHA ID
        file_name: the name of the file

    Returns:
        string containing the contents of the file in git

    Raises:
        CalledProcessError: when the git command fails, e.g. when the file does not exist
    """
    result = subprocess.run(
        ["git", "--no-pager", "show", f"{commit_id}:{file_name}"], stdout=subprocess.PIPE, encoding="utf-8", check=False
    )
    result.check_returncode()
    return result.stdout


def detect_file_change(
    hasher: SQLHasher, commit_id: str, file_name: str
) -> Literal["FUNCTIONAL", "NON-FUNCTIONAL", "INVALID"]:
    """Compares the hashes of versions of the same file in git

    Args:
        hasher: the SQL hasher object
        commit_id: the reference to the commit
        file_name: the name of the SQL file

    Returns:
        FUNCTIONAL if the code changed functionally
        NON-FUNCTIONAL, if the code did not change functionally, e.g. whitespace
        INVALID, if the file did not exist or the SQL could not be parsed
    """
    try:
        after = git_show_file(commit_id, file_name)
    except subprocess.CalledProcessError:
        # deleted file
        return "INVALID"

    try:
        before = git_show_file(f"{commit_id}^", file_name)
    except subprocess.CalledProcessError:
        # newly created file
        return "FUNCTIONAL"

    try:
        before_hash = hasher.hash_query(before)
        after_hash = hasher.hash_query(after)
    except sqlfluff.api.simple.APIParsingError:
        return "INVALID"
    return "FUNCTIONAL" if before_hash != after_hash else "NON-FUNCTIONAL"


hasher = SQLHasher(dialect="sparksql")
change_type = detect_file_change(hasher, "<COMMIT_ID>", "<FILE_NAME>")
if change_type == "FUNCTIONAL":
    print("The SQL query should be executed after this commit")
elif change_type == "NON-FUNCTIONAL":
    print("The SQL query does not have to be executed after this commit")
else:
    print("The query file is invalid before or after the commit (e.g. syntax error or deleted)")
