package mw.moyocare.mobile.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val Forest = Color(0xFF075C43)
val ForestDeep = Color(0xFF034632)
val Leaf = Color(0xFFB7E779)
val Mint = Color(0xFFEAF4E9)
val Canvas = Color(0xFFF4F8F2)
val Ink = Color(0xFF20332C)
val MutedInk = Color(0xFF708078)
val Border = Color(0xFFE3EAE2)
val Warning = Color(0xFFB9642B)

private val MoyoCareColors = lightColorScheme(
    primary = Forest,
    onPrimary = Color.White,
    secondary = Leaf,
    onSecondary = ForestDeep,
    background = Canvas,
    onBackground = Ink,
    surface = Color.White,
    onSurface = Ink,
    surfaceVariant = Mint,
    onSurfaceVariant = MutedInk,
    outline = Border,
    error = Color(0xFFB3261E),
)

@Composable
fun MoyoCareTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = MoyoCareColors,
        content = content,
    )
}
