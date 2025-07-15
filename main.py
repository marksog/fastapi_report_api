from enum import Enum
from fastapi import FastAPI
from pydandic import BaseModel



app = FastAPI()

# Path Parameters to get a list specific operations for potentials
class PotentialOperation(str, Enum):
    potentials = "potentials"
    potential = "potential"
    new_potential = "new_potential"
    modify_potential = "modify_potential"
    delete_potential = "delete_potential"
    convert_potential = "convert_potential"

# Path Parameters to get a list specific operations for disciples
class DisciplesOperation(str, Enum):
    disciples = "disciples"
    disciple = "disciple"
    new_disciple = "new_disciple"
    modify_disciple = "modify_disciple"
    delete_disciple = "delete_disciple"

# Login Operations
class LoginOperations(str, Enum):
    login = "login"
    logout = "logout"
    register = "register"
    modify_profile = "modify_profile"
    reset_password = "reset_password"

# Request Data Models
class PotentialContact(BaseModel):
    first_name: str
    last_name: str | None = None
    user_id: int
    contact: dict
    location: str 
    notes: str | None = None
    date: str
    disciple: bool = False 

data = {
    "potentials": [
        {
            "first_name": "John",
            "last_name": "Pope",
            "user_id": 1,
            "contact": {
                "email": "john@gmail.com",
                "phone": "+1234567890",
                "instagram": "@johnpope",
                "facebook": "john.pope",
                "twitter": "@johnpope",
                "snapchat": "johnpope123",
            },
            "location": "the place of meeting",
            "notes": "some notes about the person",
            "date": "2023-10-01"
        }    
    ],
    "disciples": [
        {
            "first_name": "John",
            "last_name": "Pope",
            "user_id": 1,
            "contact": {
                "email": "john@gmail.com",
                "phone": "+1234567890",
                "instagram": "@johnpope",
                "facebook": "john.pope",
                "twitter": "@johnpope",
                "snapchat": "johnpope123",
            },
            "location": "the place of meeting",
            "notes": "some notes about the person",
            "date": "2023-10-01"
        } 
    ]
}




# Potentials Endpoints
@app.get("/potentials")
async def get_potentials():
    """
    returns a list of potential/ contacts of pple to reach out to
    """
    return [
        {
            "first_name": "John",
            "last_name": "Pope",
            "user_id": 1,
            "contact": {
                "email": "john@gmail.com",
                "phone": "+1234567890",
                "instagram": "@johnpope",
                "facebook": "john.pope",
                "twitter": "@johnpope",
                "snapchat": "johnpope123",
            },
            "location": "the place of meeting",
            "notes": "some notes about the person",
            "date": "2023-10-01"
        }
    ]

# Potential Endpoints
# all potentials
@app.get("/potential/{potentials}")
async def get_potential(potentials: PotentialOperation):
    """
    returns all specific potential/contact details
    """
    # list of all potentials
    return []

# getting a new potential
@app.get("/potential/{potential}/{potential_id}")
async def get_new_potential(potential: PotentialOperation, potential_id: int):
    """
    returns a new potential/contact details
    """
    # a specific potential
    # data structure should return just a specific potential from data base. should potential be tied to loggeed in user\

    return {}

# creating a new potential
@app.post("/potential/{new_potential}")
async def create_potential(new_potential: PotentialOperation, potential_contact: PotentialContact):
    """
    creates a new potential/contact details
    """
    # create a new potential
    return {"message": "New potential created successfully", "potential_contact": potential_contact}

# modifying a potential
@app.put("/potential/{modify_potential}/{potential_id}")
async def modify_potential(modify_potential: PotentialOperation, potential_id: int, potential_contact: PotentialContact):
    return {}

# modifying a potential
@app.put("/potential/{modify_potential}/{potential_id}")
async def modify_potential(modify_potential: PotentialOperation, potential_id: int):
    """
    modifies a specific potential/contact details
    """
    # modify a specific potential
    return {"message": "Potential modified successfully", "potential_contact": potential_contact}

# converting a potential to a disciple
@app.put("/potential/{convert_potential}/{potential_id}")
async def convert_potential(convert_potential: PotentialOperation, potential_id: int):
    """
    converts a specific potential/contact details to a disciple
    """
    # convert a specific potential to a disciple
    # logic to change disciple field to True
    return {"message": "Potential converted to disciple successfully"}

# deleting a potential
@app.delete("/potential/{delete_potential}/{potential_id}")
async def delete_potential(delete_potential: PotentialOperation, potential_id: int):    
    """
    deletes a specific potential/contact details
    """
    # delete a specific potential
    return {"message": "Potential deleted successfully"}

# Disciples Endpoints
# all disciples
@app.get("/disciples/{disciples}")
async def get_disciples(disciples: DisciplesOperation):
    """
    returns a list of disciples
    """
    # list of all disciples
    return [
        {"message": "List of disciples retrieved successfully"}
    ]

# getting a specific disciple
@app.get("/disciple/{disciple_id}")
async def get_disciple(disciple_id: int):
    """
    returns a specific disciple details
    """
    # a specific disciple
    return {
        "message": "Disciple details retrieved successfully"
    }

# creating a new disciple
@app.post("/disciple/{new_disciple}")
async def create_disciple(new_disciple: DisciplesOperation):
    """
    creates a new disciple
    """
    # create a new disciple
    return {"message": "New disciple created successfully"}

# modifying a disciple
@app.put("/disciple/{modify_disciple}/{disciple_id}")
async def modify_disciple(modify_disciple: DisciplesOperation, disciple_id: int):
    """
    modifies a specific disciple details
    """
    # modify a specific disciple
    return {"message": "Disciple modified successfully"}

# deleting a disciple
@app.delete("/disciple/{delete_disciple}/{disciple_id}")
async def delete_disciple(delete_disciple: DisciplesOperation, disciple_id: int):
    """
    deletes a specific disciple details
    """
    # delete a specific disciple
    return {"message": "Disciple deleted successfully"}


# login Endpoints
@app.post("/login")
async def login(login: LoginOperations):
    """
    logs in a user
    """
    # login logic here
    return {"message": "User logged in successfully"}

@app.post("/logout")
async def logout(logout: LoginOperations):
    """
    logs out a user
    """
    # logout logic here
    return {"message": "User logged out successfully"}

# register a new user
@app.post("/register")
async def register(register: LoginOperations):
    """
    registers a new user
    """
    # registration logic here
    return {"message": "User registered successfully"}

@app.put("/modify_profile")
async def modify_profile(modify_profile: LoginOperations):
    """
    modifies user profile
    """
    # modify profile logic here
    return {"message": "User profile modified successfully"}

# reset user password
@app.post("/reset_password")
async def reset_password(reset_password: LoginOperations):
    """
    resets user password
    """
    # reset password logic here
    return {"message": "User password reset successfully"}

