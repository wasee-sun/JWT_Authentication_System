'use server';
import { 
  verifyEmail,
  requestEmailVerification,
  getUsers,
  getUser,
  createUser,
  updateUser,
  deleteUser,
  activateUser,
  deactivateUser,
  uploadProfileImage
} from "@/libs/api";


export const signUpError = async (response) => {
  if (typeof response.error === "object") {
    const errorMessages = {};

    if (response.error.email) {
      errorMessages['email'] = response.error.email[0][0].toUpperCase() + 
      response.error.email[0].slice(1).toLowerCase();
    }

    if (response.error.username) {
      errorMessages['username'] = response.error.username[0][0].toUpperCase() + 
      response.error.username[0].slice(1).toLowerCase();
    }

    if (response.error.first_name) {
      errorMessages['first_name'] = response.error.first_name[0][0].toUpperCase() + 
      response.error.first_name[0].slice(1).toLowerCase();
    }

    if (response.error.last_name) {
      errorMessages['last_name'] = response.error.last_name[0][0].toUpperCase() + 
      response.error.last_name[0].slice(1).toLowerCase();
    }

    if (response.error.phone_number) {
      errorMessages['phone_number'] = response.error.phone_number[0][0].toUpperCase() + 
      response.error.phone_number[0].slice(1).toLowerCase();}

    // Check for each possible attribute and append its messages
    if (response.error.password) {
      const passErrorMessages = [];
      const error = response.error.password;

      if (error.short) {
        passErrorMessages.push(...[error.short]);
      };
      if (error.upper) {
        passErrorMessages.push(...[error.upper]);
      };
      if (error.lower) {
        passErrorMessages.push(...[error.lower]);
      };
      if (error.number) {
        passErrorMessages.push(...[error.number]);
      };
      if (error.special) {
        passErrorMessages.push(...[error.special]);
      };
      
      if (passErrorMessages.length === 0) {
        passErrorMessages.push(...[error[0][0].toUpperCase() + error[0].slice(1).toLowerCase()]);
      };

      errorMessages['password'] = passErrorMessages.join(" ");
    };

    // Combine messages into a single string with \n between each
    return { error: errorMessages };
  }
  // If it's not an object, return the error as is (string or other type)
  return { error: response.error };
};

export const verifyEmailAction = async (token, expiry) => {
  try {
    const response = await verifyEmail(token, expiry);

    if (response.error) {
      return { error: response.error };
    };
    
    return { success: true };
  } catch (error) {
    console.error(error);
    return { error: error.message || "Token expired or invalid." };
  };
};

export const requestEmailVerificationAction = async (formData) => {
  const data = {
    email: formData.get("email"),
  };

  try {
    const response = await requestEmailVerification(data);
    
    if (response.error) {
      return { error: response.error };
    };

    return { success: true }; 
  } catch (error) {
    console.error(error);
    return { error: error.message || "Failed to send verification link." }
  }
};

export const getUsersAction = async () => {
  try {
    const response = await getUsers();

    if (response.error) {
      return { error: response.error };
    };

    return { users: response.data };
  } catch (error) {
    console.error(error);
    return { error: error.message || "Failed to fetch users." }
  }
};

export const getUserAction = async (id) => {
  try {
    const response = await getUser(id);

    if (response.error) {
      return { error: response.error };
    };

    return { user: response.data };
  } catch (error) {
    console.error(error);
    return { error: error.message || "Failed to fetch user." }
  }
};

export const createUserAction = async (formData) => {
  const email = formData.get("email");
  const username = formData.get("username");
  const first_name = formData.get("first_name");
  const last_name = formData.get("last_name");
  const phone_number = formData.get("phone_number");
  const password = formData.get("password");
  const c_password = formData.get("c_password");

  const errors = {};

  if (!email) {
    errors.email = "Email is required.";
  } else if (!email.includes('@')) {
    errors.email = "Invalid email format.";
  }

  if (!password) {
    errors.password = "Password is required.";
  }

  if (!c_password) {
    errors.c_password = "Password confirmation is required.";
  }

  if (password !== c_password) {
    errors.c_password = "Passwords do not match.";
  }

  if (Object.keys(errors).length > 0) {
    return { error: errors };
  }

  const data = {
    email,
    ...(username && { username }),
    ...(first_name && { first_name }),
    ...(last_name && { last_name }),
    ...(phone_number && { phone_number }),
    password,
    c_password
  };

  try {
    const response = await createUser(data);

    if (response.error) {
      return signUpError(response);
    };
    
    return { success: response.success };
  } catch (error) {
    console.error(error);
    return { error: error.message || "Failed to create user." };
  };
};

export const updateUserAction = async (id, formData) => {
  const username = formData.get("username");
  const first_name = formData.get("first_name");
  const last_name = formData.get("last_name");
  const phone_number = formData.get("phone_number");

  const data = {
    ...(username && { username }),
    ...(first_name && { first_name }),
    ...(last_name && { last_name }),
    ...(phone_number && { phone_number }),
  };

  try {
    const response = await updateUser(id, data);

    if (response.error) {
      return { error: response.error };
    };

    return { success: response.success };
  } catch (error) {
    console.error(error);
    return { error: error.message || "Failed to update user." };
  };
};

export const deleteUserAction = async (id) => {
  try {
    const response = await deleteUser(id);

    if (response.error) {
      return { error: response.error };
    };

    return { success: response.success };
  } catch (error) {
    console.error(error);
    return { error: error.message || "Failed to delete user." };
  };
};

export const activateUserAction = async (id) => {
  try {
    const response = await activateUser(id);

    if (response.error) {
      return { error: response.error };
    };

    return { success: response.success };
  } catch (error) {
    console.error(error);
    return { error: error.message || "Failed to activate user." };
  };
};

export const deactivateUserAction = async (id) => {
  try {
    const response = await deactivateUser(id);

    if (response.error) {
      return { error: response.error };
    };

    return { success: response.success };
  } catch (error) {
    console.error(error);
    return { error: error.message || "Failed to deactivate user." };
  };
};

export const uploadProfileImageAction = async (id, formData) => {
  const data = {
    profile_img: formData.get("profile_img"),
  };

  try {
    const response = await uploadProfileImage(id, data);

    if (response.error) {
      return { error: response.error };
    };

    return { success: response.success };
  } catch (error) {
    console.error(error);
    return { error: error.message || "Failed to upload profile image." };
  };
};