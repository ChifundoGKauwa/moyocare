package mw.moyocare.mobile.data

import com.google.gson.JsonParser
import kotlinx.coroutines.CancellationException
import retrofit2.Response
import java.io.IOException

class AuthRepository(
    private val api: AuthApi,
    private val tokenStore: SecureTokenStore,
) {
    val hasSession: Boolean
        get() = tokenStore.hasSession()

    suspend fun signIn(email: String, password: String): Result<Unit> = try {
        val response = try {
            api.login(LoginRequest(email.trim().lowercase(), password))
        } catch (error: IOException) {
            throw LoginFailure("Could not connect. Check your connection and try again.")
        }
        if (!response.isSuccessful) {
            val serverMessage = extractErrorMessage(response)
            if (response.code() == 401 || response.code() == 400) {
                throw LoginFailure(
                    serverMessage ?: "Email or password is incorrect, or this account is inactive.",
                )
            }
            throw LoginFailure(
                serverMessage ?: "Sign in failed. Please try again (${response.code()}).",
            )
        }
        val tokens = response.body() ?: throw LoginFailure("The server returned an empty response.")
        if (!tokenStore.save(tokens)) {
            throw LoginFailure("Could not securely save your session on this device.")
        }
        Result.success(Unit)
    } catch (error: CancellationException) {
        throw error
    } catch (error: Exception) {
        Result.failure(
            if (error is LoginFailure) error else LoginFailure("Sign in failed. Please try again."),
        )
    }

    fun signOut() = tokenStore.clear()

    private fun extractErrorMessage(response: Response<*>): String? = try {
        val body = response.errorBody()?.string()
        if (!body.isNullOrBlank()) {
            val json = JsonParser.parseString(body)
            if (json.isJsonObject) {
                val obj = json.asJsonObject
                if (obj.has("detail")) {
                    obj.get("detail").asString
                } else if (obj.has("non_field_errors") && obj.get("non_field_errors").isJsonArray) {
                    obj.getAsJsonArray("non_field_errors").firstOrNull()?.asString
                } else {
                    val firstEntry = obj.entrySet().firstOrNull()
                    if (firstEntry != null) {
                        val valElem = firstEntry.value
                        if (valElem.isJsonArray) {
                            valElem.asJsonArray.firstOrNull()?.asString
                        } else if (valElem.isJsonPrimitive) {
                            valElem.asString
                        } else null
                    } else null
                }
            } else null
        } else null
    } catch (_: Exception) {
        null
    }
}

class LoginFailure(message: String) : Exception(message)
