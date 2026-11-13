package mw.moyocare.mobile.ui

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import mw.moyocare.mobile.data.AuthRepository
import mw.moyocare.mobile.data.LoginViewModel
import mw.moyocare.mobile.data.MoyoCareApi
import mw.moyocare.mobile.data.SecureTokenStore

enum class Destination {
    ONBOARDING,
    LOGIN,
    DASHBOARD,
    PATIENTS,
    FIELD,
    SYNC,
    REGISTER_PATIENT,
}

@Composable
fun MoyoCareApp() {
    val context = LocalContext.current
    val tokenStore = remember { SecureTokenStore(context.applicationContext) }
    val repository = remember {
        AuthRepository(
            api = MoyoCareApi.auth(context.applicationContext),
            tokenStore = tokenStore,
        )
    }
    val loginViewModel: LoginViewModel = viewModel(
        factory = remember(repository) { LoginViewModel.Factory(repository) },
    )
    val loginState by loginViewModel.state.collectAsState()
    var destination by remember {
        mutableStateOf(
            if (repository.hasSession) Destination.DASHBOARD else Destination.ONBOARDING,
        )
    }

    LaunchedEffect(loginState.isSignedIn) {
        if (loginState.isSignedIn) destination = Destination.DASHBOARD
    }

    Surface(modifier = Modifier.fillMaxSize()) {
        when (destination) {
            Destination.ONBOARDING -> OnboardingScreen {
                destination = Destination.LOGIN
            }
            Destination.LOGIN -> LoginScreen(
                state = loginState,
                onSignIn = loginViewModel::signIn,
                onBack = { destination = Destination.ONBOARDING },
            )
            Destination.REGISTER_PATIENT -> PatientRegistrationScreen(
                onBack = { destination = Destination.PATIENTS },
            )
            else -> MainShell(
                destination = destination,
                onNavigate = { destination = it },
                onRegisterPatient = { destination = Destination.REGISTER_PATIENT },
                onSignOut = {
                    loginViewModel.signOut()
                    destination = Destination.LOGIN
                },
            )
        }
    }
}

@Composable
private fun MainShell(
    destination: Destination,
    onNavigate: (Destination) -> Unit,
    onRegisterPatient: () -> Unit,
    onSignOut: () -> Unit,
) {
    MainScaffold(
        selected = destination,
        onNavigate = onNavigate,
        content = {
            when (destination) {
                Destination.PATIENTS -> PatientsScreen(onRegisterPatient, onSignOut)
                Destination.FIELD -> FieldScreen(onSignOut)
                Destination.SYNC -> SyncScreen(onSignOut)
                else -> DashboardScreen(onSignOut)
            }
        },
    )
}
