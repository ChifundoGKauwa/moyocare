package mw.moyocare.mobile.data

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class LoginUiState(
    val isLoading: Boolean = false,
    val isSignedIn: Boolean = false,
    val errorMessage: String? = null,
)

class LoginViewModel(
    private val repository: AuthRepository,
) : ViewModel() {
    private val mutableState = MutableStateFlow(LoginUiState())
    val state: StateFlow<LoginUiState> = mutableState.asStateFlow()

    fun signIn(email: String, password: String) {
        if (email.isBlank() || password.isBlank()) {
            mutableState.value = LoginUiState(errorMessage = "Enter your email and password.")
            return
        }
        viewModelScope.launch {
            mutableState.value = LoginUiState(isLoading = true)
            val result = repository.signIn(email, password)
            mutableState.value = result.fold(
                onSuccess = { LoginUiState(isSignedIn = true) },
                onFailure = { LoginUiState(errorMessage = it.message) },
            )
        }
    }

    fun signOut() {
        repository.signOut()
        mutableState.value = LoginUiState()
    }

    class Factory(
        private val repository: AuthRepository,
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(LoginViewModel::class.java))
            return LoginViewModel(repository) as T
        }
    }
}
