package mw.moyocare.mobile.data

import android.content.Context
import mw.moyocare.mobile.BuildConfig
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class AuthHeaderInterceptor(
    private val tokenStore: SecureTokenStore,
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val request = chain.request().newBuilder().apply {
            tokenStore.accessToken()?.let { header("Authorization", "Bearer $it") }
        }.build()
        return chain.proceed(request)
    }
}

object MoyoCareApi {
    fun auth(context: Context): AuthApi {
        val tokenStore = SecureTokenStore(context.applicationContext)
        val client = OkHttpClient.Builder()
            .addInterceptor(AuthHeaderInterceptor(tokenStore))
            .build()
        val baseUrl = BuildConfig.API_BASE_URL.let {
            if (it.endsWith('/')) it else "$it/"
        }
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(AuthApi::class.java)
    }
}
