'''
Campus Fitness Center Management - OOP Version

Refactored from procedural to object-oriented design.

Features:
- Manage members (add, list, update status)
- Manage classes (create, list, enroll members)
- Manage trainer schedules
- Simple billing with membership-type-based discounts

Data is stored in a FitnessCenter manager backed by Member, FitnessClass,
and Trainer dataclasses.
'''

import sys
from dataclasses import dataclass, field

# Constants ----------------------------------------------------------------

VALID_MEMBERSHIP_TYPES = ('student', 'faculty', 'community')
VALID_DIFFICULTIES = ('beginner', 'intermediate', 'advanced')
BASE_CLASS_FEE = 10.0
DISCOUNT_RATES = {'student': 0.5, 'faculty': 0.75, 'community': 1.0}

# Dataclasses --------------------------------------------------------------

@dataclass
class Member:
    id: int
    name: str
    membership_type: str
    active: bool = True
    balance: float = 0.0

    def class_fee(self) -> float:
        return BASE_CLASS_FEE * DISCOUNT_RATES.get(self.membership_type, 1.0)


@dataclass
class FitnessClass:
    id: int
    name: str
    difficulty: str
    capacity: int
    enrolled_ids: list = field(default_factory=list)

    @property
    def is_full(self) -> bool:
        return len(self.enrolled_ids) >= self.capacity


@dataclass
class Trainer:
    id: int
    name: str
    specialty: str
    schedule: list = field(default_factory=list)


# FitnessCenter manager ----------------------------------------------------

class FitnessCenter:
    def __init__(self):
        self.members: list[Member] = []
        self.fitness_classes: list[FitnessClass] = []
        self.trainers: list[Trainer] = []
        self._next_member_id = 1
        self._next_class_id = 1
        self._next_trainer_id = 1

    def add_member(self, name: str, membership_type: str) -> Member:
        member = Member(id=self._next_member_id, name=name, membership_type=membership_type)
        self.members.append(member)
        self._next_member_id += 1
        return member

    def find_member(self, member_id: int) -> Member | None:
        return next((m for m in self.members if m.id == member_id), None)

    def add_class(self, name: str, difficulty: str, capacity: int) -> FitnessClass:
        fitness_class = FitnessClass(id=self._next_class_id, name=name, difficulty=difficulty, capacity=capacity)
        self.fitness_classes.append(fitness_class)
        self._next_class_id += 1
        return fitness_class

    def find_class(self, class_id: int) -> FitnessClass | None:
        return next((c for c in self.fitness_classes if c.id == class_id), None)

    def add_trainer(self, name: str, specialty: str, schedule: list) -> Trainer:
        trainer = Trainer(id=self._next_trainer_id, name=name, specialty=specialty, schedule=schedule)
        self.trainers.append(trainer)
        self._next_trainer_id += 1
        return trainer

    def find_trainer(self, trainer_id: int) -> Trainer | None:
        return next((t for t in self.trainers if t.id == trainer_id), None)


# Utility functions --------------------------------------------------------

def read_int(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = int(input(prompt))
            if min_value is not None and value < min_value:
                print(f'Please enter a value >= {min_value}')
                continue
            if max_value is not None and value > max_value:
                print(f'Please enter a value <= {max_value}')
                continue
            return value
        except ValueError:
            print('Please enter a valid integer.')


def read_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print('Input cannot be empty.')


def read_choice(prompt: str, valid: tuple, default: str) -> str:
    value = input(prompt).strip().lower()
    if value not in valid:
        print(f"Unknown value. Defaulting to '{default}'.")
        return default
    return value


def pause():
    input('\nPress Enter to continue...')


def run_menu(title: str, options: list) -> None:
    back = len(options) + 1
    while True:
        print(f'\n=== {title} ===')
        for i, (label, _) in enumerate(options, 1):
            print(f'{i}. {label}')
        print(f'{back}. Back')
        choice = read_int('Choice: ', min_value=1, max_value=back)
        if choice == back:
            break
        options[choice - 1][1]()
        pause()


# Member-related functions -------------------------------------------------

def add_member(fc: FitnessCenter):
    print('\n=== Add New Member ===')
    name = read_nonempty('Name: ')
    membership_type = read_choice(
        f'Membership type ({"/".join(VALID_MEMBERSHIP_TYPES)}): ',
        VALID_MEMBERSHIP_TYPES,
        'community',
    )

    member = fc.add_member(name, membership_type)
    print(f'Member added with id {member.id}')


def list_members(fc: FitnessCenter, show_details=True):
    print('\n=== Members ===')
    if not fc.members:
        print('No members found.')
        return
    for m in fc.members:
        if show_details:
            status = 'Active' if m.active else 'Inactive'
            print(
                f'[{m.id}] {m.name} ({m.membership_type}, {status}) '
                f'Balance: ${m.balance:.2f}'
            )
        else:
            print(f'[{m.id}] {m.name}')
    print()


def deactivate_member(fc: FitnessCenter):
    print('\n=== Deactivate Member ===')
    list_members(fc, show_details=False)
    mid = read_int('Enter member id to deactivate: ')
    member = fc.find_member(mid)
    if member is None:
        print('Member not found.')
        return
    if not member.active:
        print('Member is already inactive.')
        return
    member.active = False
    print(f'Member {member.name} is now inactive.')


def add_charge_to_member(fc: FitnessCenter):
    print('\n=== Add Charge to Member ===')
    list_members(fc, show_details=False)
    mid = read_int('Enter member id to charge: ')
    member = fc.find_member(mid)
    if member is None:
        print('Member not found.')
        return
    try:
        amount = float(input('Charge amount: $'))
    except ValueError:
        print('Invalid amount.')
        return
    member.balance += amount
    print(f"Added ${amount:.2f} to {member.name}'s balance.")


def apply_payment_from_member(fc: FitnessCenter):
    print('\n=== Record Payment ===')
    list_members(fc, show_details=False)
    mid = read_int('Enter member id: ')
    member = fc.find_member(mid)
    if member is None:
        print('Member not found.')
        return
    try:
        amount = float(input('Payment amount: $'))
    except ValueError:
        print('Invalid amount.')
        return
    member.balance -= amount
    print(f'Recorded payment of ${amount:.2f} from {member.name}.')


# Class-related functions --------------------------------------------------

def create_class(fc: FitnessCenter):
    print('\n=== Create Fitness Class ===')
    name = read_nonempty('Class name: ')
    difficulty = read_choice(
        f'Difficulty ({"/".join(VALID_DIFFICULTIES)}): ',
        VALID_DIFFICULTIES,
        'beginner',
    )
    capacity = read_int('Capacity: ', min_value=1)

    fitness_class = fc.add_class(name, difficulty, capacity)
    print(f'Fitness class created with id {fitness_class.id}')


def list_classes(fc: FitnessCenter, show_enrollment=True):
    print('\n=== Fitness Classes ===')
    if not fc.fitness_classes:
        print('No classes found.')
        return
    for c in fc.fitness_classes:
        if show_enrollment:
            print(
                f'[{c.id}] {c.name} '
                f'({c.difficulty}, capacity {c.capacity}, '
                f'enrolled {len(c.enrolled_ids)})'
            )
        else:
            print(f'[{c.id}] {c.name}')
    print()


def enroll_member_in_class(fc: FitnessCenter):
    print('\n=== Enroll Member in Class ===')
    list_members(fc, show_details=False)
    mid = read_int('Enter member id: ')
    member = fc.find_member(mid)
    if member is None:
        print('Member not found.')
        return
    if not member.active:
        print('Cannot enroll an inactive member.')
        return

    list_classes(fc, show_enrollment=False)
    cid = read_int('Enter class id: ')
    fclass = fc.find_class(cid)
    if fclass is None:
        print('Class not found.')
        return

    if fclass.is_full:
        print('Class is full.')
        return

    if mid in fclass.enrolled_ids:
        print('Member is already enrolled in this class.')
        return

    fclass.enrolled_ids.append(mid)
    print(f'Enrolled {member.name} in {fclass.name}.')

    fee = member.class_fee()
    member.balance += fee
    print(
        f'Charged ${fee:.2f} for class (base ${BASE_CLASS_FEE:.2f}, '
        f'type: {member.membership_type}).'
    )


def list_class_roster(fc: FitnessCenter):
    print('\n=== Class Roster ===')
    list_classes(fc, show_enrollment=False)
    cid = read_int('Enter class id: ')
    fclass = fc.find_class(cid)
    if fclass is None:
        print('Class not found.')
        return

    print(f'\nRoster for {fclass.name}:')
    if not fclass.enrolled_ids:
        print('No members enrolled.')
        return

    for mid in fclass.enrolled_ids:
        m = fc.find_member(mid)
        if m:
            print(f'- {m.name} ({m.membership_type})')


# Trainer-related functions ------------------------------------------------

def add_trainer(fc: FitnessCenter):
    print('\n=== Add Trainer ===')
    name = read_nonempty('Trainer name: ')
    specialty = read_nonempty('Specialty (e.g., yoga, strength, cardio): ')
    schedule = []
    print('Enter trainer availability (e.g., Mon 9-11). Leave blank to stop.')
    while True:
        slot = input('Availability: ').strip()
        if not slot:
            break
        schedule.append(slot)

    trainer = fc.add_trainer(name, specialty, schedule)
    print(f'Trainer added with id {trainer.id}')


def list_trainers(fc: FitnessCenter, show_schedule=True):
    print('\n=== Trainers ===')
    if not fc.trainers:
        print('No trainers found.')
        return
    for t in fc.trainers:
        if show_schedule:
            schedule_str = ', '.join(t.schedule) if t.schedule else 'No availability'
            print(
                f'[{t.id}] {t.name} - {t.specialty} '
                f'(Schedule: {schedule_str})'
            )
        else:
            print(f'[{t.id}] {t.name}')
    print()


def update_trainer_schedule(fc: FitnessCenter):
    print('\n=== Update Trainer Schedule ===')
    list_trainers(fc, show_schedule=False)
    tid = read_int('Enter trainer id: ')
    trainer = fc.find_trainer(tid)
    if trainer is None:
        print('Trainer not found.')
        return

    print('Current schedule:')
    for s in trainer.schedule:
        print(f'- {s}')

    print('1. Replace schedule')
    print('2. Add to schedule')
    choice = read_int('Choice: ', min_value=1, max_value=2)

    if choice == 1:
        trainer.schedule = []
        print('Enter new availability (blank to finish):')
    else:
        print('Enter additional availability (blank to finish):')

    while True:
        slot = input('Availability: ').strip()
        if not slot:
            break
        trainer.schedule.append(slot)

    print('Updated schedule:')
    for s in trainer.schedule:
        print(f'- {s}')


# Reporting / summaries ----------------------------------------------------

def show_summary_report(fc: FitnessCenter):
    print('\n=== Summary Report ===')
    total_members = len(fc.members)
    active_members = sum(1 for m in fc.members if m.active)
    total_balance = sum(m.balance for m in fc.members)

    print(f'Total members: {total_members}')
    print(f'Active members: {active_members}')
    print(f'Total outstanding balance: ${total_balance:.2f}')

    print('\nClasses:')
    for c in fc.fitness_classes:
        print(
            f'- {c.name} ({c.difficulty}): '
            f'{len(c.enrolled_ids)}/{c.capacity} enrolled'
        )

    print('\nTrainers:')
    for t in fc.trainers:
        print(f'- {t.name} ({t.specialty})')

    print()


# Menus --------------------------------------------------------------------

def member_menu(fc: FitnessCenter):
    run_menu('Member Menu', [
        ('Add member',                lambda: add_member(fc)),
        ('List members',              lambda: list_members(fc)),
        ('Deactivate member',         lambda: deactivate_member(fc)),
        ('Add charge to member',      lambda: add_charge_to_member(fc)),
        ('Record payment from member',lambda: apply_payment_from_member(fc)),
    ])


def classes_menu(fc: FitnessCenter):
    run_menu('Classes Menu', [
        ('Create fitness class',  lambda: create_class(fc)),
        ('List fitness classes',  lambda: list_classes(fc)),
        ('Enroll member in class',lambda: enroll_member_in_class(fc)),
        ('Show class roster',     lambda: list_class_roster(fc)),
    ])


def trainer_menu(fc: FitnessCenter):
    run_menu('Trainer Menu', [
        ('Add trainer',            lambda: add_trainer(fc)),
        ('List trainers',          lambda: list_trainers(fc)),
        ('Update trainer schedule',lambda: update_trainer_schedule(fc)),
    ])


def main_menu(fc: FitnessCenter):
    options = [
        ('Manage members',     lambda: member_menu(fc)),
        ('Manage classes',     lambda: classes_menu(fc)),
        ('Manage trainers',    lambda: trainer_menu(fc)),
        ('Show summary report',lambda: (show_summary_report(fc), pause())),
        ('Exit',               lambda: (print('Goodbye!'), sys.exit(0))),
    ]
    while True:
        print('\n=== Campus Fitness Center Management ===')
        for i, (label, _) in enumerate(options, 1):
            print(f'{i}. {label}')
        choice = read_int('Choice: ', min_value=1, max_value=len(options))
        options[choice - 1][1]()


if __name__ == '__main__':
    main_menu(FitnessCenter())
