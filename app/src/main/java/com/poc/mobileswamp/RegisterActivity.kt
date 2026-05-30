package com.poc.mobileswamp

import android.os.Bundle
import android.util.Patterns
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.snackbar.Snackbar
import com.poc.mobileswamp.databinding.ActivityRegisterBinding

class RegisterActivity : AppCompatActivity() {

    private lateinit var binding: ActivityRegisterBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRegisterBinding.inflate(layoutInflater)
        setContentView(binding.root)

        supportActionBar?.apply {
            title = "Create Account"
            setDisplayHomeAsUpEnabled(true)
        }

        binding.btnSubmit.setOnClickListener { validateAndSubmit() }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }

    private fun validateAndSubmit() {
        val name = binding.etName.text.toString().trim()
        val email = binding.etEmail.text.toString().trim()
        val password = binding.etPassword.text.toString()
        val confirm = binding.etConfirmPassword.text.toString()

        var valid = true

        if (name.isEmpty()) {
            binding.tilName.error = "Full name is required"
            valid = false
        } else {
            binding.tilName.error = null
        }

        if (email.isEmpty() || !Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            binding.tilEmail.error = "Enter a valid email address"
            valid = false
        } else {
            binding.tilEmail.error = null
        }

        if (password.length < 8) {
            binding.tilPassword.error = "Password must be at least 8 characters"
            valid = false
        } else {
            binding.tilPassword.error = null
        }

        if (confirm != password) {
            binding.tilConfirmPassword.error = "Passwords do not match"
            valid = false
        } else {
            binding.tilConfirmPassword.error = null
        }

        if (valid) {
            Snackbar.make(binding.root, "Account created! (PoC — not persisted)", Snackbar.LENGTH_LONG).show()
        }
    }
}
