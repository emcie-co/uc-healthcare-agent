parlant guideline create `
--condition "patient disagrees with the insurance change" `
--action "create an authorization request and notify the client of the action you did" `
--tag lBasb1M7T4

parlant guideline create `
--condition "request was made on medication status" `
--action "ask if they have enough medication until request is answered" `
--tag lBasb1M7T4

parlant journey create `
--title "Identifying Prescription Issue" `
--description "When a patient reports an issue with their prescription, first ask which specific prescription they're referring to. Once they respond, confirm the prescription name and dosage as listed in their record. Then, gather any relevant details that could help investigate the issue, such as when they attempted to fill the prescription and which pharmacy they visited. If the patient mentions anything related to insurance, check their record for recent insurance changes. If any changes are found, make sure to inform the patient accordingly." `
--condition "patient reports a prescription issue" `
--tag lBasb1M7T4

# Instruction
parlant journey create `
--title "Identifying Prescription Issue" `
--description "This process focuses on identifying and clarifying issues patients encounter with their prescriptions. It involves confirming which prescription is affected, verifying its details against the patient's medical records, and gathering relevant context such as recent pharmacy visits or refill attempts. If insurance-related concerns are raised, it also includes checking for recent changes in insurance coverage and communicating those changes back to the patient.The interaction should happen in steps, not by asking all questions at once. Start with identifying the prescription in question, confirm the details, then gradually gather more context based on what the patient shares. " `
--condition "patient reports a prescription issue" `
--tag lBasb1M7T4

# Description
parlant journey update `
--id BiYuoerl41 `
--title "Identifying Prescription Issue" `
--description "This process focuses on identifying and clarifying issues patients encounter with their prescriptions. It involves confirming which prescription is affected, verifying its details against the patient's medical records, and gathering relevant context such as recent pharmacy visits or refill attempts. If insurance-related concerns are raised, it also includes checking for recent changes in insurance coverage and communicating those changes back to the patient.The interaction should happen in steps, not by asking all questions at once. Start with identifying the prescription in question, confirm the details, then gradually gather more context based on what the patient shares."

# Multi-Step
parlant journey update `
--id BiYuoerl41 `
--title "Identifying Prescription Issue" `
--description "When a patient raises an issue with a prescription, begin by asking which specific medication they’re referring to. Once identified, confirm the prescription name and dosage as listed in their medical record to ensure alignment. After confirmation, gradually gather more details, such as when they attempted to fill the prescription, which pharmacy they visited, and whether they experienced a delay, denial, or other issue. If the patient brings up anything related to insurance, check their records for recent changes in coverage or formulary status. If any updates are found, communicate them clearly to the patient. Throughout the interaction, avoid overwhelming the patient by asking everything at once, instead, move step by step, letting the conversation flow naturally based on their responses."
