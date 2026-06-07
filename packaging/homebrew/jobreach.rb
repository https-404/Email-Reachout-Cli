class Jobreach < Formula
  include Language::Python::Virtualenv

  desc "CLI for AI-assisted job outreach over Gmail"
  homepage "https://github.com/https-404/Email-Reachout-Cli"
  url "https://github.com/https-404/Email-Reachout-Cli/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/jobreach", "--help"
  end
end
