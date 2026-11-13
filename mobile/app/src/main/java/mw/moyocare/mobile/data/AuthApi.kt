package mw.moyocare.mobile.data

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

data class LoginRequest(
    val email: String,
    val password: String,
)

data class RefreshRequest(
    val refresh: String,
)

data class TokenPair(
    val access: String,
    val refresh: String,
)

interface AuthApi {
    @POST("auth/token/")
    suspend fun login(@Body request: LoginRequest): Response<TokenPair>

    @POST("auth/token/refresh/")
    suspend fun refresh(@Body request: RefreshRequest): Response<TokenPair>
}
