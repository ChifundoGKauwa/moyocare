package mw.moyocare.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.enableEdgeToEdge
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import mw.moyocare.mobile.ui.MoyoCareApp
import mw.moyocare.mobile.ui.theme.MoyoCareTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MoyoCareTheme {
                MoyoCareApp()
            }
        }
    }
}
