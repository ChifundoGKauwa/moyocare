package mw.moyocare.mobile.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Add
import androidx.compose.material.icons.outlined.ArrowBack
import androidx.compose.material.icons.outlined.CalendarToday
import androidx.compose.material.icons.outlined.ChevronRight
import androidx.compose.material.icons.outlined.CloudDone
import androidx.compose.material.icons.outlined.CloudUpload
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.PeopleAlt
import androidx.compose.material.icons.outlined.CalendarMonth
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material.icons.outlined.MoreVert
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material.icons.outlined.Sync
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import mw.moyocare.mobile.ui.theme.Border
import mw.moyocare.mobile.ui.theme.Forest
import mw.moyocare.mobile.ui.theme.ForestDeep
import mw.moyocare.mobile.ui.theme.Ink
import mw.moyocare.mobile.ui.theme.Leaf
import mw.moyocare.mobile.ui.theme.Mint
import mw.moyocare.mobile.ui.theme.MutedInk
import mw.moyocare.mobile.ui.theme.Warning

@Composable
fun MainScaffold(
    selected: Destination,
    onNavigate: (Destination) -> Unit,
    content: @Composable () -> Unit,
) {
    val items = listOf(
        Destination.DASHBOARD to ("Home" to Icons.Outlined.Home),
        Destination.PATIENTS to ("Patients" to Icons.Outlined.PeopleAlt),
        Destination.FIELD to ("Field" to Icons.Outlined.CalendarMonth),
        Destination.SYNC to ("Sync" to Icons.Outlined.Sync),
    )
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(mw.moyocare.mobile.ui.theme.Canvas)
            .padding(top = WindowInsets.statusBars.asPaddingValues().calculateTopPadding()),
    ) {
        Box(modifier = Modifier.weight(1f)) { content() }
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .padding(start = 20.dp, end = 20.dp, top = 10.dp)
                .padding(bottom = WindowInsets.navigationBars.asPaddingValues().calculateBottomPadding()),
            color = ForestDeep,
            shape = RoundedCornerShape(28.dp),
            shadowElevation = 8.dp,
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 7.dp, vertical = 6.dp),
                horizontalArrangement = Arrangement.SpaceAround,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                for ((destination, item) in items) {
                    val (label, icon) = item
                    val active = selected == destination ||
                        (selected == Destination.REGISTER_PATIENT && destination == Destination.PATIENTS)
                    NavigationBarItem(
                        selected = active,
                        onClick = { onNavigate(destination) },
                        icon = { Icon(icon, contentDescription = label, modifier = Modifier.size(21.dp)) },
                        label = { Text(label) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = ForestDeep,
                            selectedTextColor = Leaf,
                            indicatorColor = Leaf,
                            unselectedIconColor = Color.White.copy(alpha = 0.72f),
                            unselectedTextColor = Color.White.copy(alpha = 0.72f),
                        ),
                    )
                }
            }
        }
    }
}

@Composable
fun AccountMenu(onSignOut: () -> Unit) {
    var expanded by rememberSaveable { mutableStateOf(false) }
    Box {
        IconButton(onClick = { expanded = true }) {
            Icon(Icons.Outlined.MoreVert, contentDescription = "Account options", tint = Ink)
        }
        DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            DropdownMenuItem(
                text = { Text("Sign out") },
                onClick = {
                    expanded = false
                    onSignOut()
                },
            )
        }
    }
}

@Composable
fun DashboardScreen(onSignOut: () -> Unit = {}) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
    ) {
        ScreenHeader("MoyoCare", "Community health · Preview data", { AccountMenu(onSignOut) })
        MoyoCard {
            Row(verticalAlignment = Alignment.CenterVertically) {
                PatientAvatar("HS", Modifier.size(48.dp))
                Column(modifier = Modifier.weight(1f).padding(start = 12.dp)) {
                    Text("Good morning", color = MutedInk, style = MaterialTheme.typography.bodySmall)
                    Text("Health worker", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                }
                StatusPill("Mobile preview")
            }
        }

        SectionHeading("This week", "View reports")
        Card(
            shape = RoundedCornerShape(22.dp),
            colors = CardDefaults.cardColors(containerColor = Forest),
        ) {
            Column(modifier = Modifier.padding(18.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Community health reports", color = Color.White.copy(alpha = 0.82f), style = MaterialTheme.typography.bodyMedium)
                        Text("142", color = Color.White, fontSize = 34.sp, fontWeight = FontWeight.Bold)
                    }
                    StatusPill("+12%", Leaf)
                }
                Spacer(modifier = Modifier.height(14.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    DarkMetric("Households", "86", Modifier.weight(1f))
                    DarkMetric("Visits", "48", Modifier.weight(1f))
                    DarkMetric("Flagged", "4", Modifier.weight(1f))
                }
            }
        }

        SectionHeading("Community overview", "This month")
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SummaryCard("Households", "142", "18 visited", Modifier.weight(1f))
            SummaryCard("Follow-ups", "6", "2 due today", Modifier.weight(1f))
        }

        SectionHeading("Disease trends", "View all")
        MoyoCard {
            TrendRow("Malaria", "14 reports", "↓ 8%", Forest)
            TrendRow("Respiratory", "8 reports", "↑ 3%", Warning)
            TrendRow("Diarrheal illness", "4 reports", "Stable", MutedInk)
        }

        SectionHeading("Field kit inventory", "Restock")
        MoyoCard {
            InventoryRow("ORS sachets", "24 packs", "Good", Forest)
            InventoryRow("RDT test kits", "6 boxes", "Adequate", Forest)
            InventoryRow("Paracetamol", "Low stock", "Restock soon", Warning)
        }
    }
}

@Composable
private fun DarkMetric(label: String, value: String, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .background(Color.White.copy(alpha = 0.11f), RoundedCornerShape(13.dp))
            .padding(10.dp),
    ) {
        Text(value, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 19.sp)
        Text(label, color = Color.White.copy(alpha = 0.74f), fontSize = 11.sp)
    }
}

@Composable
private fun SummaryCard(label: String, value: String, hint: String, modifier: Modifier = Modifier) {
    MoyoCard(modifier = modifier) {
        Text(label, color = MutedInk, style = MaterialTheme.typography.bodySmall)
        Spacer(modifier = Modifier.height(7.dp))
        Text(value, color = Ink, fontSize = 26.sp, fontWeight = FontWeight.Bold)
        Text(hint, color = Forest, style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun TrendRow(label: String, count: String, trend: String, color: Color) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 9.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(modifier = Modifier.size(10.dp).background(color, CircleShape))
        Text(label, modifier = Modifier.weight(1f).padding(start = 10.dp), fontWeight = FontWeight.SemiBold)
        Text(count, color = MutedInk, style = MaterialTheme.typography.bodySmall)
        Text(trend, modifier = Modifier.padding(start = 10.dp), color = color, style = MaterialTheme.typography.labelMedium)
    }
}

@Composable
private fun InventoryRow(item: String, amount: String, status: String, color: Color) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(Icons.Outlined.FavoriteBorder, contentDescription = null, tint = Forest, modifier = Modifier.size(20.dp))
        Text(item, modifier = Modifier.weight(1f).padding(start = 10.dp), style = MaterialTheme.typography.bodyMedium)
        Text(amount, color = MutedInk, style = MaterialTheme.typography.bodySmall)
        Text(status, modifier = Modifier.padding(start = 9.dp), color = color, style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
fun PatientsScreen(
    onRegisterPatient: () -> Unit,
    onSignOut: () -> Unit = {},
) {
    val names = listOf(
        Triple("Grace Phiri", "Household A · Chilinde Village", "Follow-up due"),
        Triple("Chimwemwe Zulu", "Household B · Kachere", "Stable"),
        Triple("Tamara Gondwe", "Household D · Chinsapo", "New patient"),
        Triple("Chisomo Banda", "Household F · Area 25", "Follow-up due"),
    )
    var search by rememberSaveable { mutableStateOf("") }
    var selectedFilter by rememberSaveable { mutableStateOf("All") }
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
    ) {
        ScreenHeader("Community patients", "Sample patient directory", { AccountMenu(onSignOut) })
        OutlinedTextField(
            value = search,
            onValueChange = { search = it },
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text("Search name or village") },
            leadingIcon = { Icon(Icons.Outlined.Search, contentDescription = null) },
            singleLine = true,
            shape = RoundedCornerShape(15.dp),
            colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = Forest),
        )
        Row(modifier = Modifier.fillMaxWidth().padding(vertical = 14.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf("All", "Follow-up", "New", "Stable").forEach { filter ->
                FilterPill(filter, selectedFilter == filter) { selectedFilter = filter }
            }
        }
        Card(
            colors = CardDefaults.cardColors(containerColor = Forest),
            shape = RoundedCornerShape(20.dp),
        ) {
            Column(modifier = Modifier.padding(17.dp)) {
                Text("PATIENT DIRECTORY", color = Leaf, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
                Text("142 households", color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(5.dp))
                Text("18 visited this month · 6 follow-ups", color = Color.White.copy(alpha = 0.78f), style = MaterialTheme.typography.bodySmall)
                Spacer(modifier = Modifier.height(14.dp))
                Button(onClick = onRegisterPatient, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(14.dp)) {
                    Icon(Icons.Outlined.Add, contentDescription = null)
                    Text("  Register patient")
                }
            }
        }
        SectionHeading("Patients", "142 total")
        names.filter { patient ->
            val matchesSearch = patient.first.contains(search, ignoreCase = true) ||
                patient.second.contains(search, ignoreCase = true)
            val matchesFilter = when (selectedFilter) {
                "Follow-up" -> patient.third == "Follow-up due"
                "New" -> patient.third == "New patient"
                "Stable" -> patient.third == "Stable"
                else -> true
            }
            matchesSearch && matchesFilter
        }
            .forEach { (name, detail, status) -> PatientListCard(name, detail, status) }
        Spacer(modifier = Modifier.height(12.dp))
    }
}

@Composable
private fun PatientListCard(name: String, detail: String, status: String) {
    MoyoCard(modifier = Modifier.padding(bottom = 10.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            PatientAvatar(name.split(" ").mapNotNull { it.firstOrNull() }.take(2).joinToString(""))
            Column(modifier = Modifier.weight(1f).padding(start = 12.dp)) {
                Text(name, fontWeight = FontWeight.Bold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                Text(detail, color = MutedInk, style = MaterialTheme.typography.bodySmall, maxLines = 1, overflow = TextOverflow.Ellipsis)
                Spacer(modifier = Modifier.height(7.dp))
                StatusPill(status, if (status == "Follow-up due") Warning else Forest)
            }
            Icon(Icons.Outlined.ChevronRight, contentDescription = "Open patient", tint = MutedInk)
        }
    }
}

@Composable
private fun FilterPill(text: String, selected: Boolean, onClick: () -> Unit) {
    Surface(
        modifier = Modifier.clickable(onClick = onClick),
        color = if (selected) Forest else Color.White,
        shape = RoundedCornerShape(50),
        border = if (selected) null else androidx.compose.foundation.BorderStroke(1.dp, Border),
    ) {
        Text(
            text,
            modifier = Modifier.padding(horizontal = 13.dp, vertical = 8.dp),
            color = if (selected) Color.White else MutedInk,
            style = MaterialTheme.typography.labelMedium,
        )
    }
}

@Composable
fun FieldScreen(onSignOut: () -> Unit = {}) {
    Column(modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        ScreenHeader("Field schedule", "Sample visit plan", { AccountMenu(onSignOut) })
        Card(
            colors = CardDefaults.cardColors(containerColor = Forest),
            shape = RoundedCornerShape(21.dp),
        ) {
            Column(modifier = Modifier.padding(18.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("TODAY'S FIELD PLAN", color = Leaf, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
                        Text("Household visits", color = Color.White, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                    }
                    Text("4 / 8", color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Bold)
                }
                Spacer(modifier = Modifier.height(12.dp))
                Text("Area 25 · Lilongwe", color = Color.White.copy(alpha = 0.8f))
            }
        }
        SectionHeading("Route & timeline", "8 planned visits")
        listOf(
            "Grace Phiri" to "08:30 AM · Follow-up visit",
            "Chimwemwe Zulu" to "10:00 AM · Household check",
            "Tamara Gondwe" to "01:00 PM · New registration",
            "Community water point" to "02:30 PM · Inspection",
        ).forEachIndexed { index, (name, details) ->
            ScheduleCard(name, details, index == 0)
        }
        MoyoCard(modifier = Modifier.padding(top = 6.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Outlined.LocationOn, contentDescription = null, tint = Forest)
                Text("Field kit inventory", modifier = Modifier.weight(1f).padding(start = 10.dp), fontWeight = FontWeight.SemiBold)
                Icon(Icons.Outlined.ChevronRight, contentDescription = null, tint = MutedInk)
            }
        }
    }
}

@Composable
private fun ScheduleCard(name: String, details: String, current: Boolean) {
    MoyoCard(modifier = Modifier.padding(bottom = 9.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier.size(38.dp).background(if (current) Mint else Border, CircleShape),
                contentAlignment = Alignment.Center,
            ) {
                Icon(Icons.Outlined.CalendarToday, contentDescription = null, tint = Forest, modifier = Modifier.size(19.dp))
            }
            Column(modifier = Modifier.weight(1f).padding(start = 12.dp)) {
                Text(details, color = MutedInk, style = MaterialTheme.typography.labelSmall)
                Text(name, fontWeight = FontWeight.Bold)
            }
            if (current) StatusPill("Start") else Icon(Icons.Outlined.ChevronRight, contentDescription = null, tint = MutedInk)
        }
    }
}

@Composable
fun SyncScreen(onSignOut: () -> Unit = {}) {
    Column(modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        ScreenHeader("Sync & surveillance", "Sample sync preview", { AccountMenu(onSignOut) })
        Card(
            colors = CardDefaults.cardColors(containerColor = Forest),
            shape = RoundedCornerShape(22.dp),
        ) {
            Column(modifier = Modifier.fillMaxWidth().padding(19.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("OFFLINE READY", color = Leaf, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
                        Text("4 encounters pending", color = Color.White, fontSize = 23.sp, fontWeight = FontWeight.Bold)
                    }
                    Icon(Icons.Outlined.CloudUpload, contentDescription = null, tint = Leaf, modifier = Modifier.size(32.dp))
                }
                Text("Last synced today at 8:42 AM", color = Color.White.copy(alpha = 0.75f), style = MaterialTheme.typography.bodySmall)
                Spacer(modifier = Modifier.height(14.dp))
                Button(onClick = {}, enabled = false, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(14.dp)) {
                    Icon(Icons.Outlined.Sync, contentDescription = null)
                    Text("  Sync setup in progress")
                }
            }
        }
        SectionHeading("Community trends", "Full report")
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SummaryCard("Malaria", "14", "↑ 2 this week", Modifier.weight(1f))
            SummaryCard("Diarrhea", "8", "↓ 1 this week", Modifier.weight(1f))
        }
        SectionHeading("Pending encounters", "4 reports")
        listOf(
            "Thankando Kamwendo" to "Household A · 10:42 AM",
            "Noah Mayo" to "Chilinde Village · 09:18 AM",
            "Azima Zulu" to "Household C · Yesterday",
            "Chisomo Banda" to "Area 25 · Yesterday",
        ).forEach { (name, detail) ->
            MoyoCard(modifier = Modifier.padding(bottom = 9.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    PatientAvatar(name.split(" ").mapNotNull { it.firstOrNull() }.take(2).joinToString(""))
                    Column(modifier = Modifier.weight(1f).padding(start = 12.dp)) {
                        Text(name, fontWeight = FontWeight.SemiBold)
                        Text(detail, color = MutedInk, style = MaterialTheme.typography.bodySmall)
                    }
                    StatusPill("Pending", Warning)
                }
            }
        }
        MoyoCard(modifier = Modifier.padding(top = 4.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Outlined.CloudDone, contentDescription = null, tint = Forest)
                Text("Encrypted offline storage is planned for the next step", modifier = Modifier.padding(start = 10.dp), color = MutedInk, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
fun PatientRegistrationScreen(onBack: () -> Unit) {
    var patientName by rememberSaveable { mutableStateOf("") }
    var age by rememberSaveable { mutableStateOf("") }
    var village by rememberSaveable { mutableStateOf("") }
    var actionTaken by rememberSaveable { mutableStateOf("") }
    var selectedGender by rememberSaveable { mutableStateOf("Unknown") }
    val selectedSymptoms = rememberSaveable { mutableStateOf(setOf<String>()) }

    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.Outlined.ArrowBack, contentDescription = "Back") }
            Column(modifier = Modifier.weight(1f)) {
                Text("Register patient", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                Text("Community health encounter", color = MutedInk, style = MaterialTheme.typography.bodySmall)
            }
            StatusPill("Preview")
        }
        Spacer(modifier = Modifier.height(12.dp))
        MoyoCard {
            Text("Patient details", fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(12.dp))
            FormField("Patient name", patientName, { patientName = it }, "First and last name")
            Spacer(modifier = Modifier.height(12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Column(modifier = Modifier.weight(1f)) {
                    FormField("Age", age, { age = it }, "Years", number = true)
                }
                Column(modifier = Modifier.weight(1f)) {
                    FormField("Village", village, { village = it }, "Village name")
                }
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text("Gender", style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.SemiBold)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 8.dp)) {
                listOf("Female", "Male", "Other", "Unknown").forEach { gender ->
                    FilterPill(gender, selectedGender == gender) { selectedGender = gender }
                }
            }
        }

        SectionHeading("Symptoms", "Select all that apply")
        MoyoCard {
            listOf("Fever", "Cough", "Diarrhea", "Other").forEach { symptom ->
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(
                        checked = symptom in selectedSymptoms.value,
                        onCheckedChange = { checked ->
                            selectedSymptoms.value = if (checked) {
                                selectedSymptoms.value + symptom
                            } else {
                                selectedSymptoms.value - symptom
                            }
                        },
                    )
                    Text(symptom)
                }
            }
        }

        SectionHeading("Action taken")
        MoyoCard {
            OutlinedTextField(
                value = actionTaken,
                onValueChange = { actionTaken = it },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("e.g. Given paracetamol, referred to health centre") },
                minLines = 3,
                shape = RoundedCornerShape(14.dp),
            )
        }

        Spacer(modifier = Modifier.height(16.dp))
        MoyoCard {
            Text(
                "This form is a visual preview. Patient saving and encrypted offline sync are not connected yet.",
                color = MutedInk,
                style = MaterialTheme.typography.bodySmall,
            )
        }
        Spacer(modifier = Modifier.height(18.dp))
    }
}

@Composable
private fun FormField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    number: Boolean = false,
) {
    Text(label, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.SemiBold)
    Spacer(modifier = Modifier.height(6.dp))
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = Modifier.fillMaxWidth(),
        placeholder = { Text(placeholder) },
        singleLine = true,
        shape = RoundedCornerShape(13.dp),
        keyboardOptions = androidx.compose.foundation.text.KeyboardOptions(
            keyboardType = if (number) androidx.compose.ui.text.input.KeyboardType.Number else androidx.compose.ui.text.input.KeyboardType.Text,
        ),
        colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = Forest),
    )
}
