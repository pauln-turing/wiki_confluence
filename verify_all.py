import json
import os
from datetime import datetime

# --- CONFIGURATION ---
DATA_DIRECTORY = "generated_data"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class DataVerifier:
    """A class to load and verify the consistency of the entire dataset."""

    def __init__(self, directory):
        self.directory = directory
        self.data = {}
        self.error_count = 0
        self.checks_run = 0

    def load_all_data(self):
        """Loads all JSON files from the data directory."""
        print("--- 1. Loading all data files ---")
        try:
            files_to_load = [
                "users", "spaces", "pages", "comments", "attachments",
                "space_memberships", "permissions", "labels", "page_labels"
            ]
            for file_name in files_to_load:
                path = os.path.join(self.directory, f"{file_name}.json")
                with open(path, 'r') as f:
                    self.data[file_name] = json.load(f)
                    print(f"  ✅ Loaded {file_name}.json")
            return True
        except FileNotFoundError as e:
            print(f"  ❌ ERROR: Could not load file: {e}. Aborting verification.")
            return False
        finally:
            print("-" * 50)

    def run_checks(self):
        """Runs all verification suites."""
        if not self.load_all_data():
            return

        self._verify_page_and_space_integrity()
        self._verify_permissions_logic()
        self._verify_label_scoping()
        self._verify_page_publication_state()

        self._print_summary()

    def _verify_page_and_space_integrity(self):
        """Checks consistency between pages, spaces, users, and content."""
        print("--- 2. Verifying Page and Space Integrity ---")
        initial_errors = self.error_count
        self.checks_run += 1
        
        # Pre-build a set of (user_id, space_id) for quick membership lookup
        space_members = {
            (m['user_id'], m['space_id']) for m in self.data['space_memberships'].values()
        }

        for page_id, page in self.data['pages'].items():
            space_id = page.get('space_id')
            if space_id not in self.data['spaces']:
                self._log_error(f"Page '{page_id}' points to a non-existent space '{space_id}'.")
                continue

            # Check creator membership
            creator_id = page['created_by_user_id']
            if (creator_id, space_id) not in space_members:
                self._log_error(f"Page '{page_id}' creator '{creator_id}' is not a member of space '{space_id}'.")
            
            # Check parent page consistency
            parent_id = page.get('parent_page_id')
            if parent_id and parent_id in self.data['pages']:
                parent_page = self.data['pages'][parent_id]
                if parent_page['space_id'] != space_id:
                    self._log_error(f"Page '{page_id}' and its parent '{parent_id}' are in different spaces.")

        # Check comment author membership
        for comment_id, comment in self.data['comments'].items():
            page_id = comment.get('page_id')
            if page_id in self.data['pages']:
                space_id = self.data['pages'][page_id]['space_id']
                author_id = comment['author_user_id']
                if (author_id, space_id) not in space_members:
                    self._log_error(f"Comment '{comment_id}' author '{author_id}' is not a member of the page's space '{space_id}'.")
        
        self._print_check_result(initial_errors)

    def _verify_permissions_logic(self):
        """Checks the business rules for the permissions table."""
        print("--- 3. Verifying Permissions Logic ---")
        initial_errors = self.error_count
        self.checks_run += 1

        for perm_id, perm in self.data['permissions'].items():
            user_id = perm.get('user_id')
            group_id = perm.get('group_id')
            is_active = perm.get('is_active')
            revoked_by = perm.get('revoked_by_user_id')
            revoked_at = perm.get('revoked_at')

            # Mutual exclusivity check
            if user_id and group_id:
                self._log_error(f"Permission '{perm_id}' has both user_id and group_id set.")
            if not user_id and not group_id:
                 self._log_error(f"Permission '{perm_id}' has neither user_id nor group_id set.")

            # Revocation state check
            if not is_active and (not revoked_by or not revoked_at):
                self._log_error(f"Inactive permission '{perm_id}' is missing revocation details.")
            if is_active and (revoked_by or revoked_at):
                self._log_error(f"Active permission '{perm_id}' has unnecessary revocation details.")

        self._print_check_result(initial_errors)

    def _verify_label_scoping(self):
        """Ensures labels are applied only within their designated space."""
        print("--- 4. Verifying Label Scoping ---")
        initial_errors = self.error_count
        self.checks_run += 1

        for link_key, page_label in self.data['page_labels'].items():
            page_id = page_label.get('page_id')
            label_id = page_label.get('label_id')

            if page_id in self.data['pages'] and label_id in self.data['labels']:
                page_space = self.data['pages'][page_id]['space_id']
                label_space = self.data['labels'][label_id]['space_id']
                if page_space != label_space:
                    self._log_error(f"Page Label '{link_key}' links a page in space '{page_space}' with a label from space '{label_space}'.")
        
        self._print_check_result(initial_errors)

    def _verify_page_publication_state(self):
        """Checks if a page's state matches its is_published flag."""
        print("--- 5. Verifying Page Publication State ---")
        initial_errors = self.error_count
        self.checks_run += 1

        for page_id, page in self.data['pages'].items():
            state = page.get('state')
            is_published = page.get('is_published')

            if state == 'published' and not is_published:
                self._log_error(f"Page '{page_id}' has state 'published' but is_published is false.")
            if state in ['draft', 'archived'] and is_published:
                self._log_error(f"Page '{page_id}' has state '{state}' but is_published is true.")
        
        self._print_check_result(initial_errors)

    def _log_error(self, message):
        """Prints an error message and increments the counter."""
        print(f"  ❌ ERROR: {message}")
        self.error_count += 1
    
    def _print_check_result(self, initial_error_count):
        if self.error_count == initial_error_count:
            print("  ✅ OK: All checks passed for this section.")
        print("-" * 50)

    def _print_summary(self):
        """Prints the final verification summary."""
        print("\n--- Verification Summary ---")
        if self.error_count == 0:
            print(f"🎉 SUCCESS: All {self.checks_run} verification suites passed without errors!")
        else:
            print(f"🚨 FAILED: Found {self.error_count} inconsistency issue(s) across {self.checks_run} suites. Please review the errors above.")

if __name__ == "__main__":
    verifier = DataVerifier(DATA_DIRECTORY)
    verifier.run_checks()
